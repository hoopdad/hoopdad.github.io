"""Authenticate the recorded servicing task union, instructions and limits."""

from think_fast_tests.workflows.guards import Definition

CASE_ID = "insurance-policy-servicing"
ROLE_IDS = (
    "service-intake", "policy-terms", "billing-reconciliation",
    "correspondence-draft", "service-review",
)


def load_definition(corpus, prompt_id):
    definition = Definition.from_corpus(corpus, CASE_ID, prompt_id)
    if tuple(role.role_id for role in definition.case.roles) != ROLE_IDS:
        raise ValueError("servicing source role mismatch")
    return definition
