"""Explicit five-Agent claims collaboration and case-bound service."""

from think_fast_tests.agent_workflows.execution import WorkflowService as DomainWorkflowService

from . import (
    adjuster_review, claim_intake, coverage_review, evidence_reconciliation,
    recovery_review,
)
from .definition import CASE_ID

MODULES = (
    claim_intake, evidence_reconciliation, coverage_review,
    recovery_review, adjuster_review,
)


def create_agents(client_factory, tools_factory):
    """Factories receive role_id and (role_id, client), respectively."""
    agents = {}
    for module in MODULES:
        client = client_factory(module.ROLE_ID)
        agents[module.ROLE_ID] = module.create_agent(
            client, tools_factory(module.ROLE_ID, client))
    return agents


class WorkflowService(DomainWorkflowService):
    def __init__(self, root, *, case_id=CASE_ID, provider=None, journal_root=None):
        if case_id != CASE_ID:
            raise ValueError("claims service is case-bound")
        super().__init__(root, case_id=case_id, provider=provider, journal_root=journal_root)
