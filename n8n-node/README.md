# n8n-nodes-signatrust

[![npm version](https://img.shields.io/npm/v/n8n-nodes-signatrust.svg)](https://www.npmjs.com/package/n8n-nodes-signatrust)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![n8n Community Node](https://img.shields.io/badge/n8n-Community%20Node-orange)](https://docs.n8n.io/integrations/community-nodes/)

This is the official **n8n Community Node** for **[Signatrust](https://signatrust.net)** — the trust, verification, and accountability layer for autonomous AI agents.

It allows you to generate, verify, and retrieve cryptographically signed **AI Decision Receipts** directly within your n8n workflows, creating independently verifiable evidence of every AI agent decision — without exposing prompts, outputs, or sensitive business data.

---

## Features

| Operation | Description |
|---|---|
| **Generate Decision Receipt** | Create a cryptographically signed receipt for an AI agent decision |
| **Verify Decision Receipt** | Verify the authenticity and integrity of an existing receipt |
| **Get Decision Receipt** | Retrieve the full details of a receipt by its ID |

---

## AI Agent Agnostic

This node works with **any AI integration** in n8n. Pass the output of any AI node directly to Signatrust:

| AI Integration | Expression |
|---|---|
| OpenAI / GPT-4o | `{{ $json.message.content }}` |
| LangChain Agent | `{{ $json.output }}` |
| Anthropic Claude | `{{ $json.content[0].text }}` |
| Google Gemini | `{{ $json.candidates[0].content.parts[0].text }}` |
| n8n AI Agent Node | `{{ $json.output }}` |
| Any HTTP Request | `{{ $json }}` |

---

## How it works

Place the Signatrust node **immediately after** any AI decision node in your workflow:

```
[Trigger] → [AI Agent] → [Signatrust: Generate Receipt] → [Continue workflow]
```

Signatrust returns a `receipt_id`, cryptographic `hash`, `signature`, and a public `verify_url`. Anyone can independently verify the receipt at `https://verify.signatrust.net/r/{receipt_id}` — without accessing your system, prompts, or raw outputs.

---

## Installation

### Via n8n UI (Recommended)
1. Open your n8n instance
2. Go to **Settings → Community Nodes**
3. Click **Install**
4. Enter `n8n-nodes-signatrust`
5. Click **Install**

### Via npm
```bash
npm install n8n-nodes-signatrust
```

---

## Credentials

1. Create a free account at [signatrust.net](https://signatrust.net)
2. Navigate to your [dashboard](https://signatrust.net/dashboard) → **Settings → API Keys**
3. Generate a new API Key
4. In n8n, add a new **Signatrust API** credential and paste your key
5. *(Enterprise only)* Update the **Base URL** to your self-hosted endpoint

---

## Usage

### Generate Decision Receipt

**Required fields:**
- **Agent Name** — e.g. `LoanApprovalAgent`
- **Workflow Name** — e.g. `Loan Approval Workflow`
- **Action Taken** — e.g. `Approved loan application`
- **Decision Output** — The JSON or text output from the AI model

**Optional fields:**
- **Model Used** — e.g. `gpt-4o`
- **Input Prompt** — The prompt sent to the AI
- **Workflow ID** — Auto-populated from n8n if left empty
- **Tags** — Comma-separated tags for categorization

**Returns:**
```json
{
  "receipt_id": "rcpt_a1b2c3d4e5f6",
  "signature": "c4bceca61d45f2aa...",
  "hash": "911c1146fcece20e...",
  "verify_url": "https://verify.signatrust.net/r/rcpt_a1b2c3d4e5f6",
  "timestamp": "2026-06-26T11:04:47.265Z",
  "status": "created"
}
```

### Verify Decision Receipt

Verify that a receipt has not been tampered with since it was generated.

```json
{
  "receipt_id": "rcpt_a1b2c3d4e5f6",
  "valid": true,
  "agent_name": "LoanApprovalAgent",
  "timestamp": "2026-06-26T11:04:47.265Z",
  "reason": "Signature and hash verified successfully"
}
```

### Get Decision Receipt

Retrieve the full details of a receipt by its ID.

---

## Example Workflow

An example workflow JSON is included: [`example-workflow.json`](./example-workflow.json)

It demonstrates:
- Calling OpenAI to evaluate a loan application
- Generating a Signatrust receipt for the AI decision
- Returning both the AI output and the signed receipt

---

## Compatibility

- **n8n version**: 1.0.0 or later
- **Node.js**: 18 or later
- **Signatrust API**: v1

---

## Support & Documentation

- **Website**: [signatrust.net](https://signatrust.net)
- **API Documentation**: [signatrust.net/docs/api](https://signatrust.net/docs/api)
- **Dashboard**: [signatrust.net/dashboard](https://signatrust.net/dashboard)
- **Enterprise inquiries**: [partners@signatrust.net](mailto:partners@signatrust.net)
- **Issues**: [GitHub Issues](https://github.com/abokenan444/Signatrust/issues)

---

## License

[MIT](LICENSE) © [Signatrust](https://signatrust.net)
