# Signatrust

**The trust, verification, and accountability layer for autonomous AI agents.**

[signatrust.net](https://signatrust.net) | [API Docs](https://signatrust.net/docs/api) | [Dashboard](https://signatrust.net/dashboard) | [partners@signatrust.net](mailto:partners@signatrust.net)

---

## What is Signatrust?

Signatrust provides a platform for generating and verifying cryptographically signed AI Decision Receipts. Each receipt creates independently verifiable evidence of autonomous AI actions — without exposing prompts, outputs, or sensitive business data.

Every AI decision becomes a verifiable fact.

---

## Why Signatrust?

| Capability | Description |
|---|---|
| **Cryptographically signed receipts** | Every AI decision is signed with a tamper-evident cryptographic hash |
| **Tamper-evident verification** | Any party can independently verify a receipt without accessing raw data |
| **Independent auditability** | Receipts are verifiable by regulators, clients, and auditors without system access |
| **Privacy-preserving design** | Verification does not require exposing prompts, model outputs, or business logic |
| **Cloud and Enterprise deployment** | Available as Signatrust Cloud or fully self-hosted Enterprise |
| **API-first architecture** | Integrate with any system via a simple REST API |
| **AI Agent agnostic** | Works with any AI model, framework, or orchestration platform |

---

## Repositories

| Directory | Description |
|---|---|
| [`n8n-node/`](./n8n-node/) | Official n8n Community Node — first production integration |
| `signatrust-core/` | Core platform and APIs *(coming soon)* |
| `examples/` | Sample workflows and integration patterns *(coming soon)* |
| `docs/` | Specifications, ADR examples, and compliance guides *(coming soon)* |

---

## Integrations

**Available now:**

[![n8n](https://img.shields.io/badge/n8n-Community%20Node-orange)](https://www.npmjs.com/package/n8n-nodes-signatrust)

**Coming soon:**

- CrewAI
- LangChain
- OpenAI Agents SDK
- Anthropic Claude Tool Use
- MCP (Model Context Protocol)

Signatrust is built as a universal trust layer — not a plugin for a single platform. The n8n node is the first integration in a broader ecosystem designed to work with any AI agent infrastructure.

---

## How it works

```
[AI Agent makes a decision]
        ↓
[POST /v1/receipts — Signatrust API]
        ↓
[Returns: receipt_id + signature + hash + verify_url]
        ↓
[Anyone can verify at: https://verify.signatrust.net/r/{receipt_id}]
```

No raw prompts, no model outputs, no sensitive data leaves your system. Only the signed evidence of the decision.

---

## Quick Start

Install the n8n Community Node:

```
Settings → Community Nodes → Install → n8n-nodes-signatrust
```

Or via npm:

```bash
npm install n8n-nodes-signatrust
```

See [`n8n-node/README.md`](./n8n-node/README.md) for full documentation.

---

## Contact

- **Website**: [signatrust.net](https://signatrust.net)
- **API Documentation**: [signatrust.net/docs/api](https://signatrust.net/docs/api)
- **Enterprise inquiries**: [partners@signatrust.net](mailto:partners@signatrust.net)

---

© 2026 [Signatrust](https://signatrust.net) — MIT License
