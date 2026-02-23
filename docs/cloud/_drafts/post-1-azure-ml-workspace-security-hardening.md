# Post 1: Azure ML Workspace Security Hardening (Detailed Checklist)

This post documents the **specific controls** we implemented in Azure Machine Learning (AML), why they matter, and how we verify them. We are sharing this externally so other teams can use it as a practical blueprint for deploying a more secure AML environment.

> Scope: AML workspace, associated storage/key vault/ACR, compute identities, private endpoint patterns, DNS resolution, and network boundary controls.

## 1) Identity-first workspace access model

### 1.1 Control objective
Eliminate static credentials and enforce least privilege via Microsoft Entra identities and Azure RBAC.

### 1.2 What we configured
- Enabled managed identity on workspace (system-assigned and/or user-assigned based on environment pattern).
- Assigned RBAC at minimum required scope:
  - `Storage Blob Data Reader` or `Storage Blob Data Contributor` for data paths.
  - `ACRPull` for compute that pulls curated container images.
  - Key Vault permissions via RBAC (or equivalent access policy model where required).
- Added read-level access where needed for private endpoint-connected resource discovery and operational checks (for example, scoped `Reader` access on relevant networking/resource objects used by deployment validation and diagnostics).- Disabled the ACR admin user account on the workspace container registry; compute pulls images via managed identity (`ACRPull` role) rather than static registry credentials.- For storage file share paths, used tightly scoped file-plane access (for example, `Storage File Data Privileged Contributor` or an equivalent org-defined “File Privileged User” role).

### 1.3 Why it matters
- Removes long-lived secrets from notebooks, jobs, and pipelines.
- Reduces blast radius when one principal is compromised.
- Improves traceability of who/what accessed data.

### 1.4 Validation steps
- `az ml workspace show --name <ws> --resource-group <rg> --query identity`
- `az role assignment list --assignee <principalId> --all`
- Confirm identity can perform required private endpoint-related discovery checks without granting broad network admin rights.
- Confirm data access works with identity-based datastore auth and no embedded keys.

---

## 2) Data access hardening for training and pipelines

### 2.1 Control objective
Ensure jobs access data using identities, not cached credentials.

### 2.2 What we configured
- Datastores configured for identity-based auth where supported.
- Compute identity permissions scoped to required storage containers/paths.
- User identity mode used only where job-level accountability is required.

### 2.3 Why it matters
- Prevents credential leakage from datastore definitions.
- Keeps storage authorization centralized in RBAC.
- Supports cleaner forensic trails for regulated workloads.

### 2.4 Validation steps
- Submit test job reading secured datastore path.
- Verify storage logs show expected identity principal.
- Negative test: unauthorized identity should fail with expected `403`.

---

## 3) Network isolation and exfiltration reduction

### 3.1 Control objective
Restrict ingress/egress and reduce accidental or malicious data exfiltration.

### 3.2 What we configured
- Private endpoint strategy for workspace and dependent services where feasible.
- Explicitly disabled public network access where service capabilities allowed it; where full disablement was not possible or not yet feasible, we implemented effective equivalent controls with strict firewall allowlists and trusted-path-only access.
- Firewall/network rules on storage and registry to avoid broad public exposure.
- Controlled outbound access pattern for compute.
- DNS alignment for private resolution paths, including private DNS zones, VNet links, and custom DNS forwarder/conditional forwarding rules where required by enterprise DNS architecture.
- Configured compute clusters and instances with **no public IP address** where platform support allowed; inbound job management traffic uses Azure Private Link Service rather than a public load balancer.

### 3.3 Why it matters
- Cuts public attack surface significantly.
- Prevents “shadow egress” from unmanaged routes.
- Makes data flow paths explicit and governable.

### 3.4 Validation steps
- Resolve private FQDNs from approved subnets.
- Verify blocked behavior from non-approved networks.
- Validate public endpoint access is denied (or effectively denied by policy/firewall) for workspace-associated resources.
- Validate private DNS resolution path end to end (`nslookup`/`dig` from approved network + successful private IP resolution + connectivity test).
- Confirm job lifecycle operations still function under restricted outbound rules.

---

## 4) Encryption and key governance

### 4.1 Control objective
Protect sensitive metadata and data-at-rest under enterprise key management expectations.

### 4.2 What we configured
- Evaluated/implemented customer-managed key (CMK) pattern where policy required.
- Key Vault configured with soft delete and purge protection.
- Set `enable_data_isolation: true` at workspace creation time for environments where multiple workspaces share a storage account, Key Vault, or container registry. This prefixes all artifacts with the workspace GUID and applies Azure ABAC conditions so each workspace's managed identity can only access its own containers — preventing cross-workspace data leakage in shared-resource patterns.
- Evaluated the `hbi_workspace` flag at workspace create time; enabled for workloads handling sensitive or regulated data. This reduces Microsoft diagnostic telemetry and encrypts local scratch disk on compute. The flag cannot be changed after creation.
- Documented immutable decisions made at create-time (for example, isolation/HBI choices).

### 4.3 Why it matters
- Strengthens regulatory and internal policy alignment.
- Improves lifecycle control around key rotation and crypto governance.
- Prevents late-stage redesign from immutable platform settings.

### 4.4 Validation steps
- Verify encryption mode and key references in workspace configuration.
- Validate managed identity has required key permissions (`Get`, `WrapKey`, `UnwrapKey`) where applicable.
- Test key rotation runbook in non-prod before prod rollout.

---

## 5) Operational governance and drift prevention

### 5.1 Control objective
Keep hardening persistent over time, not just at deployment day.

### 5.2 What we configured
- Azure Policy guardrails to audit/deny noncompliant workspace/network settings.
- Monitoring and alerting for identity failures, image pull failures, and data access errors.
- Standard verification playbook run after every significant infra or RBAC change.

### 5.3 Why it matters
- Prevents configuration drift from eroding security posture.
- Accelerates incident response with predictable checks.
- Produces reusable evidence for internal audit and compliance reviews.

### 5.4 Validation steps
- Policy compliance snapshot per environment.
- Weekly review of high-signal failures (`403`, auth token errors, ACR pull failures).
- Quarterly access recertification for privileged identities.

---

## Lessons learned

1. **Create-time decisions are critical**: identity and isolation architecture must be decided early.
2. **Least privilege needs iteration**: first pass is rarely perfect; tighten after telemetry.
3. **Public access hardening must be explicit**: “assumed private” is not enough without confirming public network access settings and firewall behavior.
4. **DNS is part of security, not just connectivity**: private endpoint architectures fail open operationally if name resolution is incomplete or inconsistent.
5. **Security + usability balance is real**: private networking works best with documented developer paths.

---

## References (Microsoft Learn)

- https://learn.microsoft.com/azure/machine-learning/concept-enterprise-security
- https://learn.microsoft.com/azure/machine-learning/how-to-identity-based-service-authentication
- https://learn.microsoft.com/azure/machine-learning/how-to-network-security-overview
- https://learn.microsoft.com/azure/machine-learning/how-to-managed-network
- https://learn.microsoft.com/azure/machine-learning/concept-customer-managed-keys
- https://learn.microsoft.com/azure/role-based-access-control/overview

---

## Security Configuration Reference Table

Every security-relevant configuration applied in this workspace. Names, resource groups, subscription IDs, and environment-specific identifiers are excluded.

| Configuration | Setting Applied | Security Principle | Rationale |
|---|---|---|---|
| Workspace managed identity | System-assigned or user-assigned, enabled at creation | No static credentials | Keyless service-to-service authentication; credential lifecycle managed by Entra ID |
| Storage Blob data access | `Storage Blob Data Reader` or `Storage Blob Data Contributor` on workspace storage account | Least privilege | Data-plane role only; broad control-plane (Contributor) rights not required for data operations |
| Storage File access | `Storage File Data Privileged Contributor` or equivalent file-plane role | Least privilege | File shares require a separate file-plane permission from blob; scoped to required share only |
| ACR image pull for compute | `ACRPull` on workspace container registry | Least privilege | Read-only image pull; no push credentials or admin account required on compute |
| ACR admin user | Disabled | Reduce static credential exposure | Static registry admin credentials are a frequently exploited vector; managed identity replaces them |
| Key Vault access (CMK operations) | RBAC: `Get`, `WrapKey`, `UnwrapKey` | Least privilege | Minimum permissions for customer-managed key operations; full secrets/certificates admin not required |
| Private endpoint `Reader` access for identity | Scoped `Reader` on required networking/resource objects | Least privilege | Enables PE discovery and diagnostics without granting network admin or Contributor rights |
| Key Vault soft delete | Enabled | Data protection, recoverability | Prevents accidental or malicious key deletion from immediately destroying data access |
| Key Vault purge protection | Enabled | Data protection | Prevents permanent key purge during retention window even by authorized users |
| Private endpoint — Workspace | Enabled | Network isolation | Removes public ingress to workspace control and data planes |
| Private endpoint — Storage (blob, file) | Enabled per required sub-resources | Network isolation | Storage traffic on private IP; public storage endpoint not reachable |
| Private endpoint — Key Vault | Enabled | Network isolation | Prevents key material access over public network paths |
| Private endpoint — ACR | Enabled | Network isolation | Container image pulls over private path; no public ACR access required |
| Public network access — Workspace | Disabled, or allowlisted with strict policy enforcement | Defense in depth | Explicit denial prevents accidental re-exposure via portal or ARM API |
| Public network access — Storage | Disabled + trusted Azure services exception where required for platform operations | Defense in depth | Eliminates broad internet access; trusted-services exception preserves AML platform function |
| Public network access — Key Vault | Disabled (private endpoint + selected VNet access only) | Defense in depth | Key material must not be reachable from the public internet |
| Public network access — ACR | Disabled | Defense in depth | Image pulls use private endpoint only |
| Private DNS zone — Workspace | `privatelink.api.azureml.ms`, `privatelink.notebooks.azure.net` | DNS-level network control | Without correct private DNS, private endpoint IPs are unresolvable and connections fall back to public |
| Private DNS zone — Storage | `privatelink.blob.core.windows.net`, `privatelink.file.core.windows.net` | DNS-level network control | Ensures blob and file storage FQDNs resolve to private IPs inside the VNet |
| Private DNS zone — Key Vault | `privatelink.vaultcore.azure.net` | DNS-level network control | Ensures key operations resolve to private IP |
| Private DNS zone — ACR | `privatelink.azurecr.io` | DNS-level network control | Ensures image pulls resolve to private IP |
| VNet link on all private DNS zones | Linked to deployment VNet | DNS resolution | Required for DNS zones to serve queries from VNet-resident resources |
| Conditional DNS forwarding | Configured on enterprise DNS servers for all `privatelink.*` zones | DNS resolution consistency | Prevents public fallback for PE FQDNs in environments running custom DNS infrastructure |
| No-public-IP compute | Enabled on compute clusters and instances where platform supports it | Reduced attack surface | Eliminates internet-accessible IP on compute nodes; job management uses Private Link Service |
| Identity-based datastore auth | Enabled on all datastores; no cached-credential datastores where avoidable | No embedded credentials | Avoids SAS tokens or account keys being stored in datastore definitions readable by all workspace users |
| Customer-managed keys (CMK) | Enabled where policy requires; service-side encryption preferred | Encryption control | Allows key lifecycle management independent of Microsoft; service-side reduces subscription complexity |
| Data isolation at workspace creation | `enable_data_isolation: true` for shared-resource workspace patterns | Tenant isolation | Prefixes artifacts with workspace GUID and applies ABAC conditions; prevents cross-workspace data access in shared storage/KV/ACR |
| HBI workspace flag | Evaluated at create time; enabled for sensitive workloads | Data minimization, encryption | Reduces Microsoft telemetry collection; encrypts local scratch disk; cannot change after creation |
| Azure Policy guardrails | Audit/deny for workspace network settings, private endpoint, and public access | Drift prevention | Prevents manual portal changes from silently downgrading the secure baseline |
| Monitoring and alerting | Enabled for `403` errors, auth token failures, ACR pull failures, and data access anomalies | Operational security | Provides early warning signal for misconfiguration and access control violations |
