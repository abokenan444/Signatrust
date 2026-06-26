# n8n-nodes-signatrust

[![npm version](https://img.shields.io/npm/v/n8n-nodes-signatrust.svg)](https://www.npmjs.com/package/n8n-nodes-signatrust)
[![license](https://img.shields.io/npm/l/n8n-nodes-signatrust.svg)](./LICENSE)

Sign every AI decision in your n8n workflow with **[Signatrust](https://signatrust.net)** &mdash; the trust, verification and accountability layer for autonomous AI agents.

This community node lets any n8n workflow **generate, verify and retrieve cryptographically signed AI Decision Receipts** against Signatrust Cloud or your self-hosted enterprise endpoint.

- **One unified credential** for Cloud and Self-Hosted (Connection Type selector)
- **Three focused operations** &mdash; nothing more, by design
- **Privacy-first** &mdash; raw prompts and outputs are SHA-256 hashed; only the hash is stored unless you opt in
- **MIT-licensed**, open source
- Production-deployed adapter at `https://signatrust.net/api/v1/n8n`

> Full landing page, recipes and FAQ: **<https://signatrust.net/n8n>**

---

## What this node is &mdash; and what it isn't

| Does | Doesn't |
| --- | --- |
| Cryptographically signs the AI output you hand it (Ed25519 over canonical JSON) | Stream or persist your workflow execution logs |
| Returns receipt id, signature, hash, public verify URL, full receipt | Replace n8n Enterprise Log Streaming, Audit Logs, RBAC or Workflow Monitoring |
| Hashes raw inputs/outputs server-side, storing only the hash | Send raw prompts or business data to Signatrust unless you opt in |
| Verifies and retrieves any previously sealed receipt | Embed analytics or telemetry beyond the three operations you trigger |
| Works against Cloud **or** self-hosted via one credential | Require a separate package or credential per deployment |

---

## Install

In your n8n instance go to **Settings &rarr; Community Nodes &rarr; Install** and enter:

```
n8n-nodes-signatrust
```

Or, in a self-hosted n8n:

```bash
npm install n8n-nodes-signatrust
```

Requires n8n `>= 1.0` and Node.js `>= 20`.

---

## Set up the credential

1. Sign up at <https://signatrust.net/register> &mdash; register an agent and copy the `sk_live_…` API key it issues (shown once).
2. In n8n, create a new **Signatrust API** credential.
3. Pick the **Connection Type**:
   - **Signatrust Cloud** (default) &mdash; Base URL is `https://signatrust.net/api/v1/n8n`, no further config needed.
   - **Self-Hosted Enterprise** &mdash; Base URL field appears; set it to e.g. `https://signatrust.your-company.com/api/v1/n8n`.
4. Paste the API key.
5. Click **Test** &mdash; the node hits `GET /ping` against your endpoint; a green check means the credential resolved to a live, non-suspended agent.

---

## Operations

### Generate Decision Receipt

| Field | Required | Notes |
| --- | --- | --- |
| Agent Name | yes | Display name of the AI agent that made the decision |
| Workflow Name | yes | Defaults to `{{$workflow.name}}` |
| Action Taken | yes | Short description of what the agent did |
| Decision Output | yes | The AI output. Only its SHA-256 hash is stored unless you opt in |
| AI Model / Provider / Version | no | e.g. `gpt-4o` / `openai` / `2025-08-01` |
| Input / Prompt | no | Raw prompt &mdash; only the hash is stored |
| Decision Type | no | Semantic label (e.g. `loan_decision`) |
| Risk Level | no | `low` &middot; `medium` &middot; `high` &middot; `critical` |
| Human Review Took Place | no | Boolean |
| Policies / Permissions / Tags | no | Comma-separated lists |
| Include Raw Decision in Metadata | no | Off by default &mdash; opt in to persist the raw text |

The node also automatically attaches `workflow_id`, `execution_id` and `node_name` from n8n's execution context.

Response (handed to the next n8n step verbatim):

```jsonc
{
  "ok": true,
  "receipt_id": "STR-3525207773",
  "sequence": 324,
  "timestamp": "2026-06-26T15:20:26.592Z",
  "hash": "sha256:3a58bff6...",
  "signature": "fj9FpBMPgP...",
  "public_key": "MCowBQYDK2VwAyEA0Cv4w...",
  "algorithm": "ed25519",
  "verify_url": "https://signatrust.net/api/v1/n8n/receipts/STR-3525207773/verify",
  "share_url": "https://signatrust.net/verify?id=STR-3525207773",
  "fetch_url": "https://signatrust.net/api/v1/n8n/receipts/STR-3525207773",
  "receipt": { "id": "STR-3525207773", "type": "decision_receipt", "...": "..." }
}
```

### Verify Decision Receipt

Looks up a receipt by id and returns the four-pillar verdict used on the public [verify portal](https://signatrust.net/verify):

```jsonc
{
  "ok": true,
  "receipt_id": "STR-3525207773",
  "valid": true,
  "signed": true,
  "integrity": true,
  "chain": true,
  "checks": { "hash_matches": true, "signature_valid": true, "chain_linked": true },
  "errors": [],
  "timestamp": "...",
  "sequence": 324,
  "share_url": "https://signatrust.net/verify?id=STR-3525207773"
}
```

### Get Decision Receipt

Fetches the full canonical receipt body for archival, downstream signing, or to render inside Slack / Notion / your CRM alongside the original decision.

---

## Example workflows

A minimal example workflow ships in this package as [`example-workflow.json`](./example-workflow.json). Three full recipes are documented at **<https://signatrust.net/n8n>**:

- Loan rejection &rarr; signed receipt &rarr; Slack
- Claude approval &rarr; signed receipt &rarr; CRM
- Inbound webhook &rarr; verify &rarr; IF branch &rarr; fulfilment

---

## Error handling

- `401` &mdash; missing or revoked API key
- `402` &mdash; plan quota exceeded; response carries `tier`, `used`, `limit`, `upgrade_url`
- `403` &mdash; agent suspended
- `404` &mdash; receipt id not found (on Verify / Get)

Enable **Continue On Fail** on the node to route over-quota or invalid-receipt errors to a fallback branch.

---

## Links

- **Landing page**: <https://signatrust.net/n8n>
- **REST docs**: <https://signatrust.net/docs>
- **Receipt specification (ADR v1.0)**: <https://signatrust.net/adr>
- **Discovery document**: <https://signatrust.net/.well-known/signatrust.json>
- **Public verify portal**: <https://signatrust.net/verify>
- **Source**: <https://github.com/abokenan444/Signatrust/tree/main/n8n-node>

---

## Compatibility

- n8n `>= 1.0.0`
- Node.js `>= 20`

---

## License

[MIT](LICENSE) &copy; Signatrust
