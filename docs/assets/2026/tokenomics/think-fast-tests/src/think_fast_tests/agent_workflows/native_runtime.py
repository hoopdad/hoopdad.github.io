"""Separate native domain composition; the construction API remains offline.

The Hosted GPT broker owns this object, its campaign directory and its shared
journal. A campaign is a new namespace, never an archived journal continuation.
Creating/inspecting the schedule does not send a model request.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from think_fast_tests.contracts import TestCaseRef
from think_fast_tests.corpus import load_corpus
from think_fast_tests.scheduling import build_schedule
from think_fast_tests.workflows.guards import Definition, State
from think_fast_usecase_one.client import encoded
from think_fast_usecase_one.native import LocalInferenceBoundary, NativeProvider

from .execution import Request, WorkflowService, execution_key, write_new
from .registry import CASE_IDS

ACTIVE_CASES = ("insurance-claims-evidence", "insurance-underwriting-intake")


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}", value):
        raise ValueError("invalid campaign identifier")
    return value


def validated_request(corpus, case_id, request, *, arm=None):
    if case_id not in CASE_IDS:
        raise ValueError("unregistered domain case")
    selected = Request.model_validate(request)
    if selected.repetition != 1 or arm is not None and selected.arm != arm:
        raise ValueError("single-pass selection or frontend arm mismatch")
    try:
        Definition.from_corpus(corpus, case_id, selected.prompt_id)
    except StopIteration:
        # StopIteration crossing an async Hosted handler is rewritten by
        # Python into RuntimeError. Keep a source-selection rejection explicit.
        raise ValueError("prompt does not belong to selected case") from None
    return selected


def campaign_schedule(corpus, run_id):
    identifier(run_id)
    refs = [TestCaseRef(case_id=p.case_id, prompt_id=p.prompt_id)
            for case in CASE_IDS for p in corpus.prompts if p.case_id == case]
    schedule = build_schedule(refs, run_id=run_id, seed=42, repetitions=1)
    if len(schedule.slots) != 400:
        raise ValueError("current corpus does not match authorized matrix")
    return schedule


class Campaign:
    """Fresh immutable schedule and source/settings/receiver authority.

    Only this namespace is reopened. Reservations and originals never move
    between campaigns. A different source cohort requires explicit new binding;
    this implementation rejects changes instead of implicitly merging cohorts.
    """

    def __init__(self, root, directory, *, run_id, binding, case_id=None):
        self.root = Path(root).resolve()
        self.directory = Path(directory).resolve()
        if not self.directory.is_relative_to(self.root):
            raise ValueError("campaign must remain inside runtime root")
        self.corpus = load_corpus(self.root)
        self.schedule = campaign_schedule(self.corpus, run_id)
        self.run_id = run_id
        if case_id is not None and case_id not in ACTIVE_CASES:
            raise ValueError("case not yet activated by its sprint")
        self.case_id = case_id
        self.binding = json.loads(encoded(binding))
        self.directory.mkdir(parents=True, exist_ok=True)
        manifest = {
            "contract": "native-domain-campaign-v1", "run_id": run_id,
            "schedule": self.schedule.model_dump(mode="json"), "binding": self.binding,
            "prompt_sha256": {
                f"{p.case_id}/{p.prompt_id}": p.rendered_sha256 for p in self.corpus.prompts
                if p.case_id in CASE_IDS},
        }
        path = self.directory / "campaign.json"
        if path.exists():
            original = json.loads(path.read_bytes())
            expected = {**manifest, "binding": original.get("binding")}
            if original != expected:
                raise ValueError("campaign schedule/source prompts changed; never rebind")
            if case_id not in ACTIVE_CASES[1:] and original != manifest:
                raise ValueError("campaign binding changed; lookup only, never rebind")
        else:
            if case_id in ACTIVE_CASES[1:]:
                raise ValueError("continuation requires the original current campaign")
            write_new(path, manifest)
        self.campaign_fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()
        self.fingerprint = self.campaign_fingerprint
        if case_id in ACTIVE_CASES[1:]:
            self._bind_case(case_id)

    def _bind_case(self, case_id):
        """Append a prospective cohort; never rewrite a manifest or old attempt.

        The same campaign directory and suite.db remain authoritative. A copied
        collector report is not a receipt, and missing/ambiguous prior results
        cannot open later slots. Even an empty reservation blocks reassignment.
        """
        slots = tuple(s for s in self.schedule.slots if s.case_id == case_id)
        if len(slots) != 50:
            raise ValueError("continuation requires one complete case")
        prefix = {}
        for previous in self.schedule.slots[:slots[0].position]:
            request = self._request(previous)
            directory = self.directory / execution_key(previous.case_id, request)
            result = directory / "result.json"
            original = directory / "request.json"
            if not result.is_file() or not original.is_file():
                raise ValueError("earlier campaign slot is never-sent or unresolved")
            receipt = json.loads(original.read_bytes())
            outcome = json.loads(result.read_bytes())
            if (receipt.get("request") != request
                    or receipt.get("case_id") != previous.case_id
                    or receipt.get("state_id") != previous.state_id
                    or receipt.get("execution_binding", {}).get("campaign_sha256")
                    != self.campaign_fingerprint
                    or outcome.get("status") not in {
                        "complete", "incomplete", "needs-review", "error"}):
                raise ValueError("earlier campaign slot remains unresolved or differs")
            prefix[previous.slot_id] = {
                "request_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
                "result_sha256": hashlib.sha256(result.read_bytes()).hexdigest(),
            }
        record = {
            "contract": "native-domain-case-cohort-v1",
            "campaign_sha256": self.campaign_fingerprint, "run_id": self.run_id,
            "case_id": case_id, "binding": self.binding,
            "slots": [s.model_dump(mode="json") for s in slots],
            "settled_prefix": prefix,
        }
        cohorts = self.directory / "cohorts"
        path = cohorts / (case_id + ".json")
        if path.exists():
            if json.loads(path.read_bytes()) != record:
                raise ValueError("case cohort changed; lookup only, never rebind")
        else:
            if any((self.directory / execution_key(case_id, self._request(s))).exists()
                   for s in slots):
                raise ValueError("attempted case cannot acquire a different cohort")
            cohorts.mkdir(exist_ok=True)
            write_new(path, record)
        self.fingerprint = hashlib.sha256(path.read_bytes()).hexdigest()

    def _request(self, slot):
        return dict(prompt_id=slot.prompt_id, arm=slot.arm,
                    run_id=self.run_id, pair_id=slot.pair_id, repetition=1,
                    completion_tokens=2048)

    def slot(self, case_id, request):
        if self.case_id is not None and case_id != self.case_id:
            raise ValueError("request outside active case cohort")
        selected = validated_request(self.corpus, case_id, request)
        if selected.completion_tokens != 2048:
            raise ValueError("historical campaign completion cap must remain 2048")
        if selected.run_id != self.run_id:
            raise ValueError("request outside current campaign")
        slot = next((slot for slot in self.schedule.slots
                     if (slot.case_id, slot.prompt_id, slot.arm, slot.pair_id, slot.repetition) ==
                     (case_id, selected.prompt_id, selected.arm, selected.pair_id, selected.repetition)),
                    None)
        if slot is None:
            raise ValueError("request does not match a scheduled slot")
        return slot

    def require_next(self, slot):
        from think_fast_usecase_one.campaign_fence import CampaignFence
        CampaignFence(self.root).require_open({"run_id": self.run_id})
        # A persisted attempted/result identity is never silently re-executed.
        # Unresolved attempts stop progression; ordinary terminal model failures
        # remain valid single-pass outcomes and do not require a green rerun.
        for previous in self.schedule.slots[:slot.position]:
            request = dict(prompt_id=previous.prompt_id, arm=previous.arm,
                           run_id=self.run_id, pair_id=previous.pair_id, repetition=1,
                           completion_tokens=2048)
            key = execution_key(previous.case_id, request)
            directory = self.directory / key
            result = directory / "result.json"
            if not result.is_file():
                raise ValueError("earlier campaign slot is never-sent or unresolved")
            if json.loads(result.read_bytes())["status"] in {"unknown-effect", "blocked"}:
                raise ValueError("earlier campaign slot remains unresolved")


class NativeCaseService(WorkflowService):
    """Native composition shared by campaign and selected-prompt smoke runs."""

    def __init__(self, root, *, case_id, provider, provenance, journal_root):
        if not isinstance(provider, NativeProvider):
            raise TypeError("native domain composition requires NativeProvider")
        super().__init__(root, case_id=case_id, provider=provider, journal_root=journal_root)
        self.provenance = provenance

    def _provider_allowed(self):
        return isinstance(self.provider, NativeProvider)

    @property
    def evidence_class(self):
        return "synthetic-offline" if self.provider.synthetic_only else "live-model"

    def _boundary(self, journal):
        return LocalInferenceBoundary(journal, self.clock, self.provider)

    def _provenance(self):
        return self.provenance

    async def _prepare(self):
        await self.provider.authorize()


class NativeWorkflowService(NativeCaseService):
    """Same first-class Agents/gates, distinct native composition and evidence."""

    def __init__(self, root, *, case_id, campaign, provider, provenance):
        if not isinstance(provider, NativeProvider):
            raise TypeError("native domain composition requires NativeProvider")
        if case_id not in ACTIVE_CASES or (
                case_id != ACTIVE_CASES[0] and campaign.case_id != case_id):
            raise ValueError("native service requires the active case cohort")
        super().__init__(root, case_id=case_id, provider=provider,
                         provenance=provenance, journal_root=campaign.directory)
        self.campaign, self.provenance = campaign, provenance

    def _binding(self):
        return {"campaign_sha256": self.campaign.fingerprint,
                "evidence_class": self.evidence_class}

    def _state(self, definition, selected):
        slot = self.campaign.slot(self.case_id, selected.model_dump())
        state = State(definition, selected.arm)
        state.state_id = slot.state_id
        return state

    async def execute(self, request):
        try:
            slot = self.campaign.slot(self.case_id, request)
            self.campaign.require_next(slot)
        except (ValueError, StopIteration, KeyError):
            return self._result("error", error="invalid-campaign-selection")
        return await super().execute(request)
