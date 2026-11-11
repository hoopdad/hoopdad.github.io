"""Deterministic process guards shared by both routing arms.

This module does not construct clients or infer quality from model confidence.
Its packet is an offline graph interface, not the source worker_result schema.
"""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass, field

from think_fast_tests.contracts import Prompt, UseCase


REPAIR_DEFECTS = frozenset({
    "structural", "calculation", "citation", "dependency-revision", "completeness",
})


class GuardError(ValueError):
    """Only application-owned categories are safe to render."""


def reject(reason):
    raise GuardError(reason)


def strict_json(raw: bytes):
    """Reject duplicate keys, nonfinite numbers and non-object envelopes."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                reject("duplicate-json-key")
            result[key] = value
        return result

    if not isinstance(raw, bytes):
        reject("invalid-json-bytes")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=lambda _: reject("nonfinite-json"))
    except (ValueError, UnicodeError, RecursionError):
        reject("malformed-json")
    if not isinstance(value, dict):
        reject("invalid-envelope")
    return value


def route_choice(raw: bytes, choices: tuple[str, ...], *, arm: str) -> str:
    """GPT selects; Decision-1 scores. Neither gets an extra confidence gate.

    Both forms are NORMALIZED offline graph messages, not provider wire claims.
    Decision-1's original maximum option must agree with the reported choice.
    Exact ties select the first maximum in the unchanged catalogue order.
    """
    if not isinstance(raw, bytes) or len(raw) > 65536:
        reject("route-envelope-overflow")
    value = strict_json(raw)
    if arm == "gpt":
        if set(value) != {"choice"}:
            reject("invalid-route-envelope")
    elif arm == "decision-1":
        if set(value) != {"choice", "confidence", "probabilities"}:
            reject("invalid-probability-envelope")
        confidence, probabilities = value["confidence"], value["probabilities"]
        def probability(number):
            return type(number) in {int, float} and math.isfinite(number) and 0 <= number <= 1
        if not probability(confidence) or not isinstance(probabilities, dict):
            reject("invalid-probability")
        if set(probabilities) != set(choices) or not all(
            probability(p) for p in probabilities.values()
        ):
            reject("invalid-probability")
        if abs(math.fsum(probabilities.values()) - 1) > 0.000001:
            reject("invalid-probability-sum")
        maximum = max(probabilities.values())
        winners = [choice for choice in choices if probabilities[choice] == maximum]
        if value["choice"] not in winners:
            reject("inconsistent-reported-choice")
        return winners[0]
    else:
        reject("invalid-arm")
    if not isinstance(value["choice"], str) or value["choice"] not in choices:
        reject("unknown-route")
    return value["choice"]


@dataclass(frozen=True)
class Definition:
    case: UseCase
    prompt: Prompt
    required: tuple[str, ...]
    intake: str
    review: str
    # Immutable pairs rather than sharing mutable source SOP dictionaries.
    prerequisites: tuple[tuple[str, tuple[str, ...]], ...]
    instructions: tuple[tuple[str, str], ...]
    fixture_ids: tuple[str, ...]
    version: str

    @classmethod
    def from_corpus(cls, corpus, case_id, prompt_id):
        case = next(c for c in corpus.cases if c.case_id == case_id)
        prompt = next(p for p in corpus.prompts
                      if (p.case_id, p.prompt_id) == (case_id, prompt_id))
        fixture = corpus.fixture(case_id, prompt_id)
        sop_artifact = next(a for a in corpus.artifacts
                            if a.artifact_id == fixture["sop_artifact_id"])
        sop = json.loads(corpus.files[sop_artifact.path])
        required = tuple(fixture["selected_required_workers"])
        roles = tuple(role.role_id for role in case.roles)
        if not required or len(set(required)) != len(required) or not set(required) <= set(roles):
            reject("invalid-task-union")
        support = case_id == "use-case-one"
        intake = "support-intake" if support else sop["intake_worker"]
        review = "support-review" if support else sop["review_worker"]
        dependencies = {r.role_id: tuple(r.prerequisites) for r in case.routes if r.role_id}
        # Final review depends on the entire selected union, not intake alone.
        dependencies[review] = tuple(r for r in required if r != review)
        if support:
            instructions = tuple((r.role_id, r.instructions) for r in case.roles)
        else:
            # Preserve the source common instruction and exact role text.
            instructions = tuple((w["id"], sop["common_instruction"] + "\n\n" +
                                  w["system_instruction"]) for w in sop["workers"])
            for gate in sop["additional_task_gates"]:
                role = gate["worker_id"]
                if gate.get("prerequisite_source") == "variant-level-required-workers":
                    dependencies[role] = tuple(r for r in required if r != role)
                elif role == "correspondence-draft":
                    dependencies[role] = tuple(dict.fromkeys((
                        *dependencies[role],
                        *(r for r in required if r in {"policy-terms", "billing-reconciliation"}),
                    )))
                else:
                    reject("unsupported-task-gate")
        if intake not in required or review not in required:
            reject("missing-intake-or-review")
        for role in required:
            if not set(dependencies[role]) <= set(required):
                reject("task-union-missing-prerequisite")
        # Check DAG feasibility without choosing the runtime route.
        ready = set()
        while True:
            added = {r for r in required if set(dependencies[r]) <= ready} - ready
            if not added:
                break
            ready.update(added)
        if set(required) != ready or len(required) > case.limits.worker_visits:
            reject("incompatible-task-budget")
        return cls(case, prompt, required, intake, review, tuple(dependencies.items()),
                   instructions, tuple(f["id"] for f in fixture["fixtures"]),
                   "support-graph-v1" if support else "domain-graph-v1")

    @property
    def choices(self):
        return tuple(route.choice_id for route in self.case.routes)

    def dependencies(self, role):
        return dict(self.prerequisites)[role]


@dataclass(frozen=True)
class Visit:
    role: str
    visit_id: str
    dependencies: tuple[str, ...]
    packet: bytes
    accepted: bool


@dataclass
class State:
    definition: Definition
    arm: str
    state_id: str = field(default_factory=lambda: "state-" + uuid.uuid4().hex)
    routing_occurrences: int = 0
    repeats: int = 0
    visits: list[Visit] = field(default_factory=list)
    current: dict[str, Visit] = field(default_factory=dict)
    defects: dict[str, str] = field(default_factory=dict)
    route_history: list[tuple[str | None, str | None]] = field(default_factory=list)
    reason: str | None = None
    operation: str = "running"
    business: str | None = None

    def __post_init__(self):
        if self.arm not in {"gpt", "decision-1"}:
            reject("invalid-arm")

    def note_defect(self, role: str, category: str):
        """Trusted validator API, never a router-controlled repair permission."""
        if role not in {v.role for v in self.visits} or category not in REPAIR_DEFECTS:
            reject("invalid-repair-defect")
        self.defects[role] = category

    def complete_ready(self):
        return set(self.definition.required) <= self.current.keys() and all(
            self.current[r].accepted and self.current[r].dependencies == tuple(
                self.current[d].visit_id for d in self.definition.dependencies(r)
            ) for r in self.definition.required
        )

    def legal(self, choice):
        d, limits = self.definition, self.definition.case.limits
        if choice not in d.choices:
            reject("unknown-route")
        route = next(r for r in d.case.routes if r.choice_id == choice)
        if route.terminal:
            if route.terminal == "complete" and not self.complete_ready():
                reject("premature-complete")
            return
        role = route.role_id
        if role not in d.required:
            reject("irrelevant-specialist")
        if not self.visits and role != d.intake:
            reject("intake-required")
        # Last routing occurrence is terminal-only, including for support.
        if (len(self.visits) >= limits.worker_visits
                or self.routing_occurrences >= limits.router_occurrences):
            reject("worker-budget-exhausted")
        if not set(d.dependencies(role)) <= self.current.keys():
            reject("unmet-prerequisite")
        if any(v.role == role for v in self.visits):
            if role not in self.defects:
                reject("unjustified-repeat")
            if self.repeats >= limits.repeat_visits:
                reject("repeat-budget-exhausted")

    def start_visit(self, role):
        """Invalidate all worker dependencies, not just calculation lineage."""
        prior = [v for v in self.visits if v.role == role]
        if prior:
            self.repeats += 1
            self.defects.pop(role, None)
        invalid = {v.visit_id for v in self.visits if v.role == role}
        while True:
            downstream = {v.visit_id for v in self.current.values()
                          if set(v.dependencies) & invalid}
            if downstream <= invalid:
                break
            invalid.update(downstream)
        for name, visit in tuple(self.current.items()):
            if visit.visit_id in invalid:
                del self.current[name]
                self.defects[name] = "dependency-revision"
        self.defects.pop(role, None)
        deps = tuple(self.current[r].visit_id for r in self.definition.dependencies(role))
        return "visit-" + uuid.uuid4().hex, deps


def accept_packet(raw: bytes, *, definition: Definition, role: str,
                  dependencies: tuple[str, ...]) -> bool:
    """Closed offline packet with explicit mandatory deliverables and limitations.

    Structural acceptance is NOT a quality verdict. The complete source-result
    schema, domain-specific evidence/safety checks and durable result export are
    still required before this interface can be used for live business work.
    """
    if len(raw) > 8192:
        reject("worker-result-overflow")
    value = strict_json(raw)
    if set(value) != {"role", "dependencies", "deliverables", "limitations", "boundary"}:
        reject("invalid-worker-packet")
    if (value["role"] != role or value["dependencies"] != list(dependencies)
            or value["boundary"] != "advisory-only-no-external-action"):
        reject("invalid-worker-binding")
    if not isinstance(value["limitations"], list) or not all(
        isinstance(text, str) and text.strip() for text in value["limitations"]
    ):
        reject("invalid-worker-limitations")
    deliverables = value["deliverables"]
    if not isinstance(deliverables, dict) or not all(
        isinstance(text, str) and text.strip() for text in deliverables.values()
    ):
        reject("invalid-worker-deliverables")
    # Review must explicitly account for EVERY case/variant/level output.
    if role == definition.review and set(deliverables) != set(definition.prompt.required_outputs):
        reject("missing-mandatory-deliverable")
    if not deliverables:
        reject("empty-worker-result")
    return True
