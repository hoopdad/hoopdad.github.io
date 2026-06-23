# the-one-prompt.md

Canonical, greenfield, one-turn build prompt for **Marginalia — Inline Annotation Copilot**
(repo: `hoopdad/marginalia`).

This file reconstructs the *final, implemented* system as a single build prompt you can hand to
one Copilot session to recreate it from scratch. It is derived from:

### 1.0 Mission

Build **Marginalia**, a Copilot-style conversational AI web app whose distinguishing feature is
**inline annotation**: instead of scrolling to the end of generated content to ask a follow-up,
the user selects a word or phrase *within* an AI response, right-clicks (or uses the selection
toolbar), types a sub-prompt, and sees the AI's answer rendered **inline, directly beneath the
selected text**, as an expandable/collapsible annotation. Annotations support multi-turn
follow-up threads. Deploy it privately to Azure in region Central US.

Operate in autopilot / no-questions mode: make reasonable assumptions and proceed without
blocking on prompts.

> **Goals vs. choices.** The product goals below are binding. The specific stack, libraries,
> repo/module breakdown, and wire formats are **not** prescribed — the team should choose whatever
> best meets the goals. A proven reference stack is listed in §1.10 for guidance only; deviate
> if you have a better path.

### Frontend — the reading & annotation experience

Build a single-page web UI for the conversational + inline-annotation experience. The team decides
the framework, libraries, and component structure. It must deliver these **goals**:

1. **Copilot-style chat.** A clean prompt/response conversation view with responses streaming in as
   they are generated.
2. **Inline annotation.** The user can select a word or phrase *inside* an AI response, invoke an
   annotation (e.g. selection toolbar or right-click), type a sub-prompt, and see the AI's answer
   appear **inline, directly beneath the selected text** — inserted at a natural break so it never
   splits a word or sentence.
3. **Multiple concurrent annotations** on the same message, each independently
   expandable/collapsible; a collapsed annotation should hint at its content (e.g. a pill showing a
   preview of the question).
4. **Follow-up threads.** Within an annotation the user can keep asking follow-up questions that
   stay scoped to the original selection and prior Q/A, streaming in place.
5. **Rich text rendering** of chat and annotation content (Markdown/GFM with code highlighting).
6. **Export the conversation** from the UI — at minimum as Markdown and as HTML — surfaced from the
   header.
7. **Dark / light theme toggle**, defaulting to the OS preference on first load and persisting the
   user's choice.
8. **"New Chat" call-to-action** placed prominently (the header).
9. **Minimalist, highly readable, accessible UX** — good keyboard support and ARIA labelling.
10. Consistent product branding throughout (the app is named **"Marginalia"**).

### Backend — API, AI, and persistence

Build an API service that powers the experience. The team decides the framework, language, and
internal structure. It must deliver these **goals**:

1. **Chat endpoint** that accepts a user message, obtains a model completion, and **streams** the
   response back to the browser token-by-token. Creating the conversation on first message and
   giving it a sensible auto-title from the opening message are expected conveniences.
2. **Annotation endpoint** that answers a sub-prompt about a selected span. To keep cost down, send
   the model only the selection plus a small window of surrounding text for context — not the whole
   conversation.
3. **Annotation follow-up endpoint** that continues an annotation thread with the original
   selection, original Q/A, and prior turns in scope.
4. **Conversation management** — list, fetch, create, and delete conversations.
5. **AI integration via Azure AI Foundry**, calling the deployed open-source model. Authenticate
   **keylessly** (managed identity / `DefaultAzureCredential`) — no API keys. Be resilient: retry
   transient failures with backoff and surface a clean error to the client if the model is
   unreachable.
6. **Persistence in Azure Blob Storage**, keyless, one stored object per conversation. Ensure the
   container exists on startup.
7. **Operational basics** — health and version endpoints, request logging, security headers, CORS,
   JSON body limits, and a central error handler.
8. **Single-origin hosting** — in production the API also serves the built frontend so one process
   answers both UI and `/api/*` (matches the container image in §1.5).
9. **Configuration via environment** — the model endpoint/deployment and the storage account URL
   are required inputs; model tuning (token limit, temperature, retries, timeout), port, CORS
   origin, and container name are optional with sensible defaults. Provide an `.env.example`.

Auth/identity for end users is out of scope for v1 — a single default user is acceptable until
identity is wired up.

### Container image

Package the whole app as a **single container image** that serves both the UI and the API from one
process (the API also hosts the built static UI). Keep the image lean (multi-stage build, runtime
dependencies only) and have it listen on one port. This is what the deploy step ships to the app
host.

### Infrastructure — Azure, private by default

Provision all cloud infrastructure as **Terraform**, kept portable across subscriptions. Assume the
operator is logged into Azure CLI as Owner/Contributor on the target subscription. The team chooses
the resource/module layout; these are the **goals and guardrails**:

**What to stand up**
- A place to **run the app** privately, that can scale down to zero when idle and back up under
  load, and that pulls its container image from a private registry.
- The **AI model**: deploy the chosen open-source, high-quality LLM through Azure AI Foundry.
- **Persistence**: an Azure Storage account with a blob container for conversations.
- **Observability**: basic logging for the app host.

**Security & access (hard requirements)**
- **Never enable public network access.** Storage, the AI service, and the app host must be
  reachable only over the private network (private endpoints / internal ingress).
- **Disable key-based auth everywhere it can be disabled** — no storage account keys, no local auth
  on the AI service. All app→service access uses **managed identity**; enforce the **highest
  practical TLS** on storage.
- Lock down inbound traffic with NSGs: **deny inbound from the internet**, allow intra-VNet, and
  allow the **VPN client pool** so an operator on the VPN can reach the private app.
- Grant least-privilege **RBAC to both** the app's managed identity **and the currently logged-in
  Azure user** (so a developer on the VPN can use the same data/AI planes): blob data access on
  storage and inference access on the AI service.

**Networking & addressing**
- This is a **spoke** that peers to the existing hub VNet and uses the hub's **centralized private
  DNS zones** for private-endpoint resolution; route private DNS for the app host so VPN clients can
  resolve it.
- **Do not hardcode IP ranges.** Choose non-overlapping CIDRs for the VNet and subnets by consulting
  **`../mikeo-lab/cidr.txt`** (the lab's CIDR inventory), and record the new allocation there. As of
  this writing that file assigns this project (`cp-annotations`) a `/22` with a private-endpoint
  subnet and a container-apps subnet (delegated to `Microsoft.App/environments`) — verify the file
  for the current values before applying, since allocations change.

**Parameterization**
- Expose SKUs/sizes and environment specifics as input variables with cheap-dev defaults: model
  name/version/SKU/capacity, app CPU/memory, location, resource group / project / environment names,
  storage account name (auto-derived when blank), the VPN client CIDR, and the hub VNet / hub DNS
  resource-group references. Provide a `*.tfvars.example`.

### 1.7 Build & deploy (local, operator-run)

Deployment is **local and operator-driven** — no CI/CD service or GitHub Actions. The agent picks
the right tool for each step at its judgement (**`azd`**, **Azure CLI**, and/or **Terraform**), but
**wraps the end-to-end flow in a single repeatable script** (e.g. `scripts/deploy.sh`) so runs are
consistent. The script should, in order:

1. Verify prerequisites and that the operator is logged into the correct subscription.
2. Provision/update infrastructure (Terraform).
3. Build the app and its container image, and push it to the private registry.
4. Roll the app host to the new image and report where it's reachable.

Keep targets (registry, app, resource group, subscription, image tag) overridable via flags or
environment variables. A separate `scripts/build.sh` for app-only builds is fine.

**Execute the deployment — don't just generate it.** Actually run the flow end-to-end against the
target subscription and **drive it to a healthy, reachable app**. Treat deployment as iterative:

- After each step, check the result; on failure, **read the actual error, diagnose the root cause,
  fix it (code, Terraform, config, sizing, or networking), and retry** until it succeeds. Do not
  stop at the first error or hand back a partially-deployed system.
- Expect and resolve real-world blockers rather than giving up — e.g. **region/SKU/quota limits**
  (switch region, SKU, or host type), **model name/format/version mismatches**, **CIDR collisions**
  (re-pick from `../mikeo-lab/cidr.txt`), **private-DNS / private-endpoint resolution**, **RBAC
  propagation delays**, and **image build/push** issues.
- **Verify health after rollout**, not just that resources were created: confirm the app responds
  on its health/version endpoint over the private network and that a basic chat + annotation round
  trip works against the deployed model and storage. If verification fails, keep remediating.
- Make changes idempotent so re-running the script converges instead of duplicating resources.
- Only report success once the live app meets the §1.9 acceptance criteria; if a blocker genuinely
  can't be resolved unattended (e.g. a missing external dependency), stop and record it clearly in
  the INPUTS_REQUIRED sense rather than reporting a false success.

### Tests

Cover both the UI and the API with automated tests, focused on the behaviors that matter: the chat
flow, the annotation / follow-up flows, persistence, and AI error handling. Tests should run with a
single command and pass in CI-free, local runs.

### Acceptance criteria

- The app is **deployed to Azure and reachable over the private network** (e.g. from the VPN),
  serving both the UI and the API from a single origin; its health/version endpoints respond and a
  basic chat + annotation round trip works against the live model and storage.
- Inline annotation works end-to-end (select → sub-prompt → streamed inline answer beneath
  selection), with multiple concurrent annotations, collapsible previews, and follow-up threads.
- Rich-text rendering, conversation export (Markdown + HTML) from the header, a persisted
  dark/light toggle, and a "New Chat" CTA are all present.
- Conversations persist to Azure Blob using **keyless** auth.
- Terraform provisions a **fully private** topology (no public network access on storage, AI, or the
  app host) with **RBAC for both the app identity and the current user**, non-overlapping CIDRs
  sourced from `../mikeo-lab/cidr.txt`, and the chosen open-source LLM (reference: Phi-4) deployed.
- The operator-run script performs the full provision → build → push → release flow locally, and
  the agent has **run it to a verified-healthy state**, remediating any deployment errors along the
  way.

