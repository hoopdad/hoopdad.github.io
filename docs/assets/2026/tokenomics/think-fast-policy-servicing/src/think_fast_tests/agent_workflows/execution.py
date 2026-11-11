"""Local first-class domain collaboration with durable shared SUITE accounting.

This does not invoke the old Worker executor or construct a live provider.
The explicit injected provider must declare synthetic_only=True.
"""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import replace
import json
import os
from pathlib import Path
from typing import Literal

from agent_framework import Message
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from think_fast_tests.contracts import DeployedProvenance, LogicalInvocation, ModelIdentity
from think_fast_tests.corpus import load_corpus
from think_fast_tests.runtime import AttemptBoundary, LocalJournal, SystemClock
from think_fast_tests.runtime.journal import OwnershipError
from think_fast_tests.tools.evidence import EvidenceSnapshot
from think_fast_tests.workflows.accounting import UnknownTurn
from think_fast_tests.workflows.dependencies import inherited_limitations
from think_fast_tests.workflows.guards import Definition, GuardError, State, Visit, route_choice, strict_json
from think_fast_tests.workflows.results import SourceResultGate
from think_fast_usecase_one.client import encoded

from .business import (
    DomainAccountedClient, DomainFrameworkEvidence, accounted_tools,
    render_final_response, source_packet, source_result_model, worker_contract, worker_session,
)
from . import registry
from .budgets import effective_definition, validate_completion_tokens
from .registered_events import notify, submitted_prompt


EXECUTION_VERSION = "whole-workflow-execution-v2"


class Request(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    prompt_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")
    arm: Literal["gpt", "decision-1"]
    run_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")
    pair_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,159}$")
    repetition: int = Field(gt=0)
    completion_tokens: Literal[2048, 8192] = 2048

    @field_validator("completion_tokens", mode="before")
    @classmethod
    def exact_completion_tokens(cls, value):
        return validate_completion_tokens(value)


def execution_key(case_id, request):
    """Existing reservation bytes, shared by producers and original readers.

    Do not switch to sorted JSON: that would abandon existing attempted slots.
    Normalization fixes field order and supplies the original default cap.
    An explicit amended cap reserves a distinct fresh operation.
    """
    normalized = Request.model_validate(request).model_dump()
    return hashlib.sha256(encoded({"case_id": case_id, **normalized})).hexdigest()


def write_new(path, value):
    with path.open("xb") as stream:
        stream.write(encoded(value))
        stream.flush()
        os.fsync(stream.fileno())


class ExecutionJournal(LocalJournal):
    def close(self):
        self._cleanup()

    def unresolved(self, operation_id):
        with self._transaction() as db:
            return db.execute(
                "SELECT 1 FROM rt_invocations WHERE operation_id=? "
                "AND status IN ('active','unknown-effect') LIMIT 1",
                (operation_id,)).fetchone() is not None


class WorkflowService:
    """Case-bound, offline-only service; repeated identities are lookup-only."""

    def __init__(self, root, *, case_id="insurance-claims-evidence",
                 provider=None, journal_root=None):
        # Validate the explicit registry binding, never an arbitrary import path.
        # Future case adapters still require their own construction/authority.
        self.package_name = registry.package_name(case_id)
        self.workflow_module = registry.workflow_module(case_id)
        if not callable(getattr(self.workflow_module, "create_agents", None)):
            raise ValueError("registered workflow requires create_agents")
        self.root = Path(root).resolve()
        self.case_id, self.provider = case_id, provider
        self.corpus = load_corpus(self.root)
        self.snapshot = EvidenceSnapshot(self.corpus, self.root / "assets/corpus")
        self.journal_root = Path(
            journal_root if journal_root is not None
            else self.root / ".runtime" / case_id / "state").resolve()
        if not self.journal_root.is_relative_to(self.root):
            raise ValueError("journal_root must remain inside repository root")
        self.clock = SystemClock()
        self._lock = asyncio.Lock()
        self._closed = False

    async def close(self):
        # The injected provider belongs to its caller. No cloud client is owned.
        self._closed = True

    def _provider_allowed(self):
        return getattr(self.provider, "synthetic_only", None) is True

    @property
    def evidence_class(self):
        return "synthetic-offline"

    def _boundary(self, journal):
        return AttemptBoundary(journal, self.clock, self.provider)

    def _provenance(self):
        return DeployedProvenance(
            submitted_revision=None, build_id=None, installed_revision=None, packages=(),
            agent_name=None, agent_version=None, runtime_principal_id=None, observed_utc=None)

    def _binding(self):
        return {"evidence_class": self.evidence_class}

    def _state(self, definition, selected):
        return State(definition, selected.arm)

    async def _prepare(self):
        pass

    def _result(self, status, *, error=None, **extra):
        return dict(
            case_id=self.case_id, status=status, response=None, metrics=[], tools=[],
            workers=[], visits=[], validation_failures=[], state_id=None,
            source_gate_receipts=[],
            final_output=None,
            execution_version=EXECUTION_VERSION,
            evidence_class=self.evidence_class, quality="unjudged",
            error=None if error is None else {"code": error}, **extra)

    async def execute(self, request):
        if self._closed:
            return self._result("blocked", error="workflow-service-closed")
        try:
            selected = Request.model_validate(request)
            definition = Definition.from_corpus(self.corpus, self.case_id, selected.prompt_id)
            definition = effective_definition(
                self.root, definition, selected.completion_tokens)
            gate = SourceResultGate.from_corpus(
                self.corpus, definition,
                profiles_raw=(self.root / "assets/source/insurance-workflow-profiles.json").read_bytes(),
                design_raw=(self.root / "assets/source/insurance-design.json").read_bytes())
            gate = replace(gate, max_bytes=None, execution_only=True)
        except (ValidationError, ValueError, StopIteration, KeyError):
            return self._result("error", error="invalid-execution-request")
        if not self._provider_allowed():
            return self._result("blocked", error="explicit-offline-provider-required")

        async with self._lock:
            normalized = selected.model_dump()
            key = execution_key(self.case_id, normalized)
            operation_id = "domain-" + key
            directory = self.journal_root / key
            directory.parent.mkdir(parents=True, exist_ok=True)
            try:
                directory.mkdir()
            except FileExistsError:
                # Never resume a reserved identity, even after process death.
                original_path = directory / "request.json"
                if (not original_path.is_file()
                        or json.loads(original_path.read_bytes()).get("execution_binding")
                        != self._binding()):
                    return self._result("unknown-effect", error="original-execution-binding-lookup-only")
                result_path = directory / "result.json"
                if result_path.is_file():
                    return json.loads(result_path.read_bytes())
                return self._result("unknown-effect", error="original-execution-lookup-only")
            state = self._state(definition, selected)
            write_new(directory / "request.json", {
                "request": normalized, "case_id": self.case_id,
                "state_id": state.state_id, "prompt_sha256": definition.prompt.rendered_sha256,
                "snapshot_sha256": gate.snapshot_sha256,
                "evidence_class": self.evidence_class,
                "execution_binding": self._binding(),
            })
            try:
                await self._prepare()
            except Exception as error:
                result = self._result(
                    "blocked", error="native-provider-preparation-failed",
                    error_detail={"type": type(error).__name__, "message": str(error)})
                write_new(directory / "result.json", result)
                return result
            journal = ExecutionJournal(self.journal_root / "suite.db")
            try:
                return await self._collaborate(
                    selected, definition, gate, state, operation_id, directory, journal)
            finally:
                journal.close()

    async def _collaborate(self, selected, definition, gate, state,
                           operation_id, directory, journal):
        try:
            owner = journal.acquire(operation_id)
        except OwnershipError:
            result = self._result("blocked", error="suite-owner-unresolved")
            write_new(directory / "result.json", result)
            return result

        request = selected.model_dump(exclude={"completion_tokens"})
        template = LogicalInvocation(
            contract_version="1.0", operation_id=operation_id,
            invocation_id="invoke-template", case_id=self.case_id, role_id="router",
            purpose="routing", evidence_class=self.evidence_class, **request)
        boundary = self._boundary(journal)
        evidence = DomainFrameworkEvidence(journal)
        execution = self.snapshot.execution(
            self.case_id, selected.prompt_id, arm=selected.arm, state_id=state.state_id)
        records, clients, sessions, failures, receipts = {}, {}, {}, [], []
        provenance = self._provenance()
        gpt = ModelIdentity(deployment="gpt-5.6-sol", model="gpt-5.6-sol",
                            version="2026-07-09", version_basis="expected")
        decision = ModelIdentity(deployment="decision-1", model="Microsoft-Decision-1",
                                 version="1", version_basis="expected")
        options = dict(boundary=boundary, template=template, owner=owner,
                       provenance=provenance, definition=definition, records=records,
                       evidence=evidence)

        def client_factory(role):
            client = DomainAccountedClient(**options, model=gpt, role=role)
            client.source_gate = gate
            clients[role] = client
            return client

        # Agents are all distinct; tools are attached to a fresh execution visit
        # only after deterministic prerequisite guards authorize that visit.
        agents = self.workflow_module.create_agents(client_factory, lambda role, client: ())
        router = DomainAccountedClient(
            **options, model=gpt if selected.arm == "gpt" else decision, purpose="routing")
        result = self._result("incomplete")
        interrupted = None
        started = self.clock.monotonic_ns()
        limits = definition.case.limits
        try:
            async with asyncio.timeout(limits.workflow_seconds):
                while state.routing_occurrences < limits.router_occurrences:
                    state.routing_occurrences += 1
                    permitted = []
                    for choice in definition.choices:
                        try:
                            state.legal(choice)
                        except GuardError:
                            continue
                        permitted.append(choice)
                    context = {
                        "case_id": self.case_id, "prompt_id": selected.prompt_id,
                        "prompt": submitted_prompt(definition.prompt.text), "state_id": state.state_id,
                        "routing_occurrence": state.routing_occurrences,
                        "choices": list(definition.choices), "legal_choices": permitted,
                        "choice_descriptions": {
                            route.choice_id: route.meaning for route in definition.case.routes},
                        "required_workers": list(definition.required),
                        "prerequisites": {r: list(definition.dependencies(r)) for r in definition.required},
                        "current": {r: strict_json(v.packet) for r, v in state.current.items()},
                        "worker_status": {
                            role: {
                                "status": ("accepted" if role in state.current else
                                           "needs-repair" if role in state.defects else "pending"),
                                "prerequisites_accepted": all(
                                    dependency in state.current
                                    for dependency in definition.dependencies(role)),
                            }
                            for role in definition.required
                        },
                        "ready_workers": [choice for choice in permitted if choice in agents],
                        "review_worker": definition.review,
                        "defects": dict(state.defects), "completion_ready": state.complete_ready(),
                        "remaining_worker_visits": limits.worker_visits - len(state.visits),
                        "remaining_repeat_visits": limits.repeat_visits - state.repeats,
                        "routing_guidance": (
                            "Choose a legal choice using executable graph progress. Pending "
                            "required workers and unresolved business facts are not terminal "
                            "execution failures. Run ready workers, repairing rejected visits "
                            "only within remaining budgets. Preserve unknown facts and advisory "
                            "limitations rather than inventing verification. Final review must "
                            "use every current required result. Complete only when "
                            "completion_ready is true; independent quality judging is separate. "
                            "Error is appropriate when no permitted work can proceed within "
                            "the remaining budgets, not merely because work is unfinished."
                        ),
                        "selection": (
                            "Return JSON {choice:<source choice>}. Select a legal choice."
                            if selected.arm == "gpt" else
                            "Score all unchanged source choices: return choice, confidence, "
                            "probabilities for every choice. Select a legal choice."),
                    }
                    router.begin(context)
                    await notify("route_start", context, router.model)
                    reply = await router.get_response(
                        [Message("user", text=encoded(context).decode())],
                        options={"max_tokens": limits.output_tokens})
                    choice = route_choice(reply.text.encode(), definition.choices, arm=selected.arm)
                    state.legal(choice)
                    await notify("route_end", context, reply, choice, router.model)
                    state.route_history.append((choice, None))
                    if choice == "error":
                        result["error"] = {"code": "router-terminal-error"}
                        break
                    if choice == "complete":
                        result["status"] = "complete"
                        final_visit = state.current[definition.review]
                        result["response"] = render_final_response(
                            final_visit.packet, version="domain-final-rendering-v2",
                            deliverables=gate.deliverables)
                        final_receipt = next(
                            receipt for receipt in receipts
                            if receipt["visit_id"] == final_visit.visit_id)
                        result["final_output"] = {
                            "rendering_version": "domain-final-rendering-v2",
                            "case_id": self.case_id, "prompt_id": selected.prompt_id,
                            "state_id": state.state_id, "operation_id": operation_id,
                            "final_review_role_id": definition.review,
                            "final_review_visit_id": final_visit.visit_id,
                            "dependency_visit_ids": list(final_visit.dependencies),
                            "source_output_sha256": final_receipt["output_sha256"],
                            "framework_output_sha256": final_receipt["framework_output_sha256"],
                            "response_sha256": hashlib.sha256(
                                result["response"].encode("utf-8")).hexdigest(),
                            "snapshot_sha256": gate.snapshot_sha256,
                        }
                        break
                    await self._visit(
                        selected, definition, gate, state, choice, agents[choice], clients[choice],
                        execution, sessions, failures, evidence, operation_id, receipts)
                else:
                    result["error"] = {"code": "routing-budget-exhausted"}
        except UnknownTurn:
            result.update(status="unknown-effect", error={"code": "lookup-only-no-repost"})
        except GuardError as error:
            result["error"] = {"code": str(error)}
        except TimeoutError:
            result["error"] = {"code": "workflow-time-budget-exhausted"}
        except BaseException as error:
            result.update(status="error", error={"code": "agent-execution-failed"})
            result["error_detail"] = {"type": type(error).__name__, "message": str(error)}
            if not isinstance(error, Exception):
                interrupted = error
        finally:
            exported = evidence.export(operation_id)
            result.update(
                state_id=state.state_id, metrics=list(records.values()),
                tools=[tool.model_dump(mode="json") for tool in exported["tools"]],
                workers=[worker.model_dump(mode="json") for worker in exported["workers"]],
                routing_occurrences=state.routing_occurrences,
                routes=[{"choice": choice, "error": error} for choice, error in state.route_history],
                visits=[dict(role=v.role, visit_id=v.visit_id,
                             dependencies=list(v.dependencies), accepted=v.accepted)
                        for v in state.visits],
                validation_failures=failures, snapshot_sha256=gate.snapshot_sha256,
                source_gate_receipts=[
                    dict(receipt, current=receipt["visit_id"] in {
                        visit.visit_id for visit in state.current.values()})
                    for receipt in receipts],
                prompt_sha256=definition.prompt.rendered_sha256,
                token_budget=router.token_binding(),
                elapsed_ms=(self.clock.monotonic_ns() - started) / 1e6,
                journal_path=str(journal.path),
            )
            if journal.unresolved(operation_id) or any(
                    a["outcome"] in {"started", "unknown-effect"} for a in records.values()):
                result.update(status="unknown-effect", response=None, final_output=None,
                              error={"code": "lookup-only-no-repost"})
            write_new(directory / "result.json", result)
            if result["status"] != "unknown-effect":
                journal.release(operation_id, owner, confirmed_terminal=True)
        if interrupted is not None:
            raise interrupted
        return result

    async def _visit(self, selected, definition, gate, state, role, agent, client,
                     execution, sessions, failures, evidence, operation_id, receipts):
        feedback = next((item for item in reversed(failures) if item["role"] == role), None)
        visit_id, dependencies = state.start_visit(role)
        evidence.invalidate(state.state_id, {v.visit_id for v in state.current.values()})
        session = worker_session(execution, role, visit_id)
        for dependency in definition.dependencies(role):
            upstream, issued = sessions[dependency]
            for fixture_id in issued:
                if fixture_id in gate.required_fixture_dependencies(role):
                    session.bind_prerequisites(upstream.completion_evidence(fixture_id))
        agent.default_options["tools"] = accounted_tools(session, client)
        binding = {
            "profile_id": self.case_id, "worker_id": role, "visit_id": visit_id,
            "snapshot_sha256": gate.snapshot_sha256,
            "dependency_visit_ids": list(dependencies),
        }
        contract = worker_contract(gate, role)
        agent.default_options["response_format"] = source_result_model(
            gate.execution_schema_bytes, binding=binding, contract=contract)
        upstream = [strict_json(state.current[r].packet)
                    for r in definition.dependencies(role)]
        context = {
            "case_id": self.case_id, "prompt_id": selected.prompt_id,
            "prompt": submitted_prompt(definition.prompt.text), "state_id": state.state_id,
            "selected_scenario": {
                "case_id": self.case_id,
                "source_variant_id": definition.prompt.source_variant_id,
                "source_level": definition.prompt.complexity.source_level,
                "required_outputs": list(definition.prompt.required_outputs),
                "guidance": (
                    "Focus on this selected prompt's supplied facts, request, scenario "
                    "constraint and required deliverables. General role instructions and "
                    "schema vocabularies describe possible variants and levels; they are "
                    "not evidence that other variants, levels or cases apply here. Do "
                    "not import their prerequisites, conflicts, deadlines or blockages. "
                    "Preserve actual missing, conflicting, freshness and authority "
                    "limitations and inherited unresolved items. Unknown source metadata "
                    "does not by itself establish that supplied scenario evidence is "
                    "missing, stale or superseded. Do not invent verification or erase "
                    "real uncertainty; retain advisory-only scope and human approval."
                ),
            },
            "role": role, "visit_id": visit_id, "dependencies": list(dependencies),
            "expected_binding": binding,
            "upstream": upstream,
            "inherited_unresolved": list(inherited_limitations(upstream)),
            "evidence_artifacts": sorted(session._allowed),
            "source_result_contract": contract,
            "validation_feedback": feedback,
            "output_contract": {
                "source_result_utf8_bytes": gate.max_bytes,
                "normalized_response_utf8_bytes": None,
                "completion_tokens": definition.case.limits.output_tokens,
                "final_review_worker": definition.review,
                "guidance": (
                    "Copy expected_binding exactly, including dependency order. Keep prose "
                    "concise and reserve room for required fields, typed claims, citations "
                    "and arrays within the completion token budget. There is no application "
                    "byte cap on the normalized model response. "
                    "Fulfill this worker's business responsibilities. Answer accuracy, "
                    "completeness and acceptability are independently evaluated after "
                    "execution; exact prose, typed business-value encodings and duplicate "
                    "deliverable labels are not execution completion requirements. "
                    "Do not regenerate all final deliverables unless this is final review. "
                    "Do not omit required findings, calculations or incident obligations to "
                    "save space. Preserve unknowns and source limitations. Use [] only for "
                    "genuinely empty arrays. A completed synthetic analysis with explicit "
                    "missing facts or unperformed real-world actions can use status advisory "
                    "and task_completion advisory-complete. Missing production acceptance "
                    "alone does not make the assigned advisory task incomplete. A failed "
                    "required tool or unfinished assigned task remains incomplete. "
                    "No truncation or automatic answer repair occurs."
                ),
            },
        }
        client.begin(context)
        raw, original, failure, source_validated = b"", None, None, False
        checked = None
        await notify("worker_start", role, visit_id)
        try:
            reply = await agent.run(encoded(context).decode())
            if client.tool_error:
                raise GuardError("tool-request-rejected")
            original = evidence.original_worker_output(state.state_id, visit_id)
            raw = source_packet(original)
            if raw != reply.text.encode():
                raise GuardError("source-framework-text-mismatch")
            checked = gate.accept(
                raw, role=role, visit_id=visit_id, dependencies=dependencies,
                evidence=evidence, state_id=state.state_id, run_id=selected.run_id,
                operation_id=operation_id)
            source_validated = True
        except GuardError as error:
            failure = str(error)
        finally:
            if original is None:
                original = evidence.original_worker_output(state.state_id, visit_id)
            if original is not None:
                evidence.worker(
                    context, original, accepted=source_validated,
                    source_validated=source_validated)
        accepted = source_validated
        await notify("worker_end", role, visit_id, accepted,
                     raw.decode("utf-8", errors="replace"),
                     strict_json(raw).get("status") if accepted else None)
        state.visits.append(Visit(role, visit_id, dependencies, raw, accepted))
        if not accepted:
            failures.append({"role": role, "visit_id": visit_id,
                             "code": failure or "missing-source-worker-output"})
            state.note_defect(role, "structural")
            return
        state.current[role] = state.visits[-1]
        receipts.append({
            "version": "domain-source-gate-receipt-v1",
            "execution_version": EXECUTION_VERSION,
            "validation_scope": "execution-integrity-only",
            "case_id": self.case_id, **selected.model_dump(exclude={"completion_tokens"}),
            "state_id": state.state_id, "operation_id": operation_id,
            "role_id": role, "visit_id": visit_id,
            "dependency_visit_ids": list(dependencies),
            "snapshot_sha256": gate.snapshot_sha256,
            "prompt_sha256": definition.prompt.rendered_sha256,
            "schema_sha256": hashlib.sha256(gate.schema_bytes).hexdigest(),
            "execution_schema_sha256": hashlib.sha256(gate.execution_schema_bytes).hexdigest(),
            "output_sha256": checked.sha256,
            "framework_output_sha256": hashlib.sha256(original).hexdigest(),
            "disposition": checked.disposition,
            "deterministic_only": True, "quality": "unjudged",
        })
        issued = []
        for fixture_id in definition.fixture_ids:
            try:
                session.completion_evidence(fixture_id)
            except (ValueError, KeyError):
                continue
            issued.append(fixture_id)
        sessions[role] = (session, tuple(issued))
