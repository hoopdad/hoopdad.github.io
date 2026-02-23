# Post 2: Microsoft Foundry Deployment Security Hardening (Detailed Checklist)

This post captures how we hardened our Microsoft Foundry deployments with emphasis on identity, model access control, runtime safety, and operational governance. We are sharing this externally so other teams can use it as a practical blueprint for deploying a more secure Foundry environment.

> Scope: Foundry project/deployment security posture, Azure OpenAI/Foundry model access patterns, private endpoint and DNS controls, and production governance controls.

## 1) Identity-based access for model invocation

### 1.1 Control objective
Remove key sprawl and force access through Entra identity + RBAC.

### 1.2 What we configured
- Preferred Microsoft Entra authentication for model calls.
- Assigned narrow roles such as:
  - `Cognitive Services OpenAI User` for inference-only consumers.
  - `Cognitive Services OpenAI Contributor` only where deployment management is required.
- Restricted role assignment scope to resource/resource group rather than broad subscription grants.
- Enabled a **custom subdomain** on each Cognitive Services / Azure OpenAI resource. This is a hard prerequisite for Microsoft Entra ID authentication to function on the endpoint; without it, only key-based auth is available. The custom subdomain is set at resource creation and cannot be changed afterward.
- Explicitly **disabled local (key-based) authentication** at the resource level where policy and tooling allowed, forcing all callers through the Entra ID path and eliminating key distribution and rotation debt.
- Added read-level access where needed for private endpoint-connected resource discovery and operational diagnostics (for example, scoped `Reader` on required networking/resource objects rather than broad network administration roles).

### 1.3 Why it matters
- Avoids long-lived API key distribution across services and repos.
- Makes access revocation immediate via RBAC changes.
- Improves auditability for who invoked and managed model endpoints.

### 1.4 Validation steps
- Test token-based inference path with `DefaultAzureCredential`.
- Confirm key-based auth is disabled/restricted per environment policy where feasible.
- Review role assignments per principal and environment.
- Confirm principals can perform required private endpoint-related validation checks without over-privileging.

---

## 2) Model and deployment governance

### 2.1 Control objective
Ensure only approved models/deployments are used in production workflows.

### 2.2 What we configured
- Defined environment-specific deployment standards (naming/versioning/approval gates).
- Limited deployment-change rights to a small operator group.
- Added rollout controls (pre-prod validation before production promotion).

### 2.3 Why it matters
- Prevents unreviewed model changes from reaching production.
- Reduces operational variance across teams.
- Improves rollback readiness during incidents.

### 2.4 Validation steps
- Confirm deployment operations require approved operator roles.
- Verify promoted deployment has matching approved artifact/version metadata.
- Execute rollback drill on non-prod cadence.

---

## 3) Safety and responsible AI controls

### 3.1 Control objective
Reduce harmful output risk and maintain acceptable-use posture in production.

### 3.2 What we configured
- Integrated responsible AI and safety expectations into release criteria.
- Enabled content safety evaluation patterns for user input and model output.
- Documented escalation paths for policy violations and abuse scenarios.

### 3.3 Why it matters
- Turns safety from “best effort” into enforceable runtime behavior.
- Improves consistency of user experience and trust outcomes.
- Supports governance readiness for legal/compliance review.

### 3.4 Validation steps
- Run curated abuse/policy test prompts in pre-prod.
- Track safety-related metrics and incident trends.
- Verify blocked/flagged behaviors map to documented policy actions.

---

## 4) Network and secret hygiene around Foundry workloads

### 4.1 Control objective
Constrain data flow and protect sensitive connection points used by Foundry applications.

### 4.2 What we configured
- Preferred private/restricted connectivity patterns where architecture supports it.
- Explicitly disabled public network access where service capabilities allowed it; where full disablement was not possible or not yet feasible, we implemented effective equivalent controls through strict firewall allowlists and trusted-path-only access.
- Applied private endpoint patterns for model-serving dependencies and associated data/services where applicable.
- Configured DNS for private resolution paths (private DNS zones, VNet links, and custom DNS forwarding/conditional forwarding rules where required by enterprise DNS design).
- Removed hardcoded credentials from app code and pipelines.
- Shifted secret retrieval to managed identity + secure stores.

### 4.3 Why it matters
- Reduces data leakage exposure from permissive networking.
- Eliminates one of the most common compromise vectors: leaked keys.
- Simplifies incident rotation/revocation procedures.

### 4.4 Validation steps
- Secret scanning across repositories/pipeline definitions.
- Connectivity tests proving approved-only network paths.
- Validate public endpoint access is denied (or effectively denied via policy/firewall) for Foundry-associated resources.
- Validate private DNS resolution end to end (`nslookup`/`dig` from approved network + expected private IP results + successful connectivity checks).
- App startup tests confirming managed identity token acquisition.

---

## 5) Continuous assurance and production operations

### 5.1 Control objective
Keep deployments secure as models, prompts, and app behavior evolve.

### 5.2 What we configured
- Policy and monitoring hooks for auth failures, unusual request patterns, and deployment drift.
- Operational runbooks for credential compromise, model rollback, and access recertification.
- Periodic control reviews tied to release cycles.

### 5.3 Why it matters
- Catches drift before it becomes an incident.
- Reduces MTTR with pre-defined response playbooks.
- Creates evidence trails that auditors and security teams can consume quickly.

### 5.4 Validation steps
- Monthly RBAC hygiene review for Foundry resources.
- Alert quality review (signal/noise tuning) for security events.
- Quarterly tabletop incident simulation for model misuse and token compromise.

---

## Lessons learned

1. **Identity-first architecture scales better** than key-based exceptions.
2. **Public network hardening must be explicit**: “private by design” needs active validation of network settings and deny paths.
3. **DNS is a security dependency** in private endpoint architectures, not a post-deployment convenience.
4. **Safety controls must be tested like code**, not documented only.
5. **Operational runbooks are part of security posture**, not optional appendices.

---

## References (Microsoft Learn)

- https://learn.microsoft.com/azure/ai-foundry/
- https://learn.microsoft.com/azure/ai-foundry/openai/how-to/managed-identity
- https://learn.microsoft.com/azure/ai-foundry/responsible-use-of-ai-overview
- https://learn.microsoft.com/azure/ai-services/content-safety/overview
- https://learn.microsoft.com/azure/role-based-access-control/overview
- https://learn.microsoft.com/azure/machine-learning/concept-enterprise-security

---

## Security Configuration Reference Table

Every security-relevant configuration applied in this Foundry deployment. Names, resource groups, subscription IDs, and environment-specific identifiers are excluded.

| Configuration | Setting Applied | Security Principle | Rationale |
|---|---|---|---|
| Authentication method | Microsoft Entra ID (token-based) as primary; key-based auth disabled or restricted | No static credentials | Entra tokens are short-lived and revocable; API keys are long-lived secrets that accumulate in repos and pipelines |
| Custom subdomain on Cognitive Services resource | Enabled at resource creation | Prerequisite for Entra auth | Entra ID authentication for Azure OpenAI / Cognitive Services requires a custom subdomain; cannot be retrofitted post-creation |
| Local (key-based) authentication | Disabled at the resource level where policy and tooling allow | Reduce static credential attack surface | Disabling keys forces all callers through the Entra identity path; eliminates key-theft as a viable attack |
| Inference role | `Cognitive Services OpenAI User` | Least privilege | Inference-only; cannot modify deployments, quotas, fine-tune models, or alter resource configuration |
| Deployment management role | `Cognitive Services OpenAI Contributor` | Least privilege, role separation | Reserved for a small operator group only; completely segregated from inference consumer identities |
| Role assignment scope | Resource or resource group (not subscription-wide) | Least privilege | Limits blast radius; a compromised identity cannot affect other Cognitive Services resources in the subscription |
| Private endpoint `Reader` access for identity | Scoped `Reader` on required networking/resource objects | Least privilege | Enables PE validation and diagnostics without granting network admin or Contributor rights |
| Managed identity for calling services/compute | System-assigned or user-assigned enabled on all app services, functions, and compute invoking Foundry | No static credentials | Removes API keys from application config, pipeline variables, and container images |
| Private endpoint — Cognitive Services / OpenAI resource | Enabled where architecture supports | Network isolation | Removes public ingress to model inference endpoint; all traffic traverses private IP path |
| Public network access — Cognitive Services resource | Disabled, or strictly allowlisted via firewall rules as effective equivalent | Defense in depth | Prevents model inference calls and management operations over public internet paths |
| Private DNS zone — Cognitive Services | `privatelink.cognitiveservices.azure.com` | DNS-level network control | Without correct private DNS, private endpoint IPs are unresolvable and connections fall back to public |
| Private DNS zone — OpenAI | `privatelink.openai.azure.com` | DNS-level network control | Ensures Azure OpenAI-specific FQDNs resolve to private IPs in Foundry deployments |
| VNet link on all private DNS zones | Linked to deployment VNet | DNS resolution | Required for DNS zones to answer queries from VNet-resident resources |
| Conditional DNS forwarding | Configured on enterprise DNS servers for `privatelink.*` zones | DNS resolution consistency | Prevents public fallback for PE FQDNs in environments with custom DNS infrastructure |
| Secret management | No hardcoded credentials in code, pipelines, or images; Key Vault integration for any non-identity secrets | Defense in depth | Eliminates the most common credential-leak path; Key Vault provides audit log and rotation capabilities |
| Deployment change rights | Restricted to small operator group holding `Cognitive Services OpenAI Contributor` | Role separation, change control | Prevents unauthorized production model changes without blocking developer inference workflows |
| Content safety integration | Enabled for input and output evaluation | Safety governance | Provides runtime enforcement of acceptable-use policy; a security control as well as an AI governance one |
| Responsible AI release criteria | Safety evaluation integrated into pre-prod release gates | Safety governance | Moves safety from aspirational to verifiable before each production promotion |
| Azure Policy guardrails | Audit/deny for network settings and public access on Cognitive Services and Foundry resources | Drift prevention | Prevents manual configuration changes from silently downgrading the security baseline |
| Monitoring and alerting | Auth failures, unusual request volume, deployment configuration drift | Operational security | Provides signal for both security incidents and model misuse patterns |
