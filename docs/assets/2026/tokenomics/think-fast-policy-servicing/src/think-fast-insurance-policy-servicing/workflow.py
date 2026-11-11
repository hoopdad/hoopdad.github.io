"""Explicit five-Agent servicing collaboration on the shared bounded runtime."""

from think_fast_tests.agent_workflows.execution import WorkflowService as DomainWorkflowService

from . import (
    service_intake, policy_terms, billing_reconciliation,
    correspondence_draft, service_review,
)
from .definition import CASE_ID

MODULES = (
    service_intake, policy_terms, billing_reconciliation,
    correspondence_draft, service_review,
)


def create_agents(client_factory, tools_factory):
    agents = {}
    for module in MODULES:
        client = client_factory(module.ROLE_ID)
        agents[module.ROLE_ID] = module.create_agent(
            client, tools_factory(module.ROLE_ID, client))
    return agents


class WorkflowService(DomainWorkflowService):
    def __init__(self, root, *, case_id=CASE_ID, provider=None, journal_root=None):
        if case_id != CASE_ID:
            raise ValueError("servicing service is case-bound")
        super().__init__(root, case_id=case_id, provider=provider, journal_root=journal_root)
