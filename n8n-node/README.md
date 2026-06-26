# n8n-nodes-signatrust

[![npm version](https://img.shields.io/npm/v/n8n-nodes-signatrust.svg)](https://www.npmjs.com/package/n8n-nodes-signatrust)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![n8n Community Node](https://img.shields.io/badge/n8n-Community%20Node-orange)](https://docs.n8n.io/integrations/community-nodes/)

This is an **n8n community node** for **[Signatrust](https://signatrust.net)**. It allows you to generate, verify, and retrieve cryptographically signed **AI Decision Receipts** for autonomous AI agents directly within your n8n workflows.

[Signatrust](https://signatrust.net) is the **trust, verification, and insurance layer for autonomous AI agents**. By using this node, you create an immutable, cryptographically verifiable audit trail of every decision your AI agents make — enabling accountability, compliance, and trust in automated systems.

---

## Features

| Operation | Description |
|---|---|
| **Generate Decision Receipt** | Create a cryptographically signed receipt for an AI agent decision |
| **Verify Decision Receipt** | Verify the authenticity and integrity of an existing receipt |
| **Get Decision Receipt** | Retrieve the full details of a receipt by its ID |

---

## How it works

Place the Signatrust node **immediately after** any AI node (OpenAI, Anthropic, LangChain, etc.) in your workflow. Pass the AI's decision output to the node, and it will:

1. Send the decision data to the [Signatrust API](https://signatrust.net/docs/api)
2. Return a `receipt_id`, cryptographic `hash`, `signature`, and a public `verify_url`
3. Allow anyone to verify the receipt at `https://verify.signatrust.net/r/{receipt_id}`

This node does **not** interfere with n8n's internal workflow logs or execution history. It operates purely on the explicit AI decision data you pass to it.

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

To use this node, you need a Signatrust API Key.

1. Create a free account at [signatrust.net](https://signatrust.net)
2. Navigate to your [dashboard](https://signatrust.net/dashboard) → **Settings → API Keys**
3. Generate a new API Key
4. In n8n, add a new **Signatrust API** credential
5. Paste your API Key
6. *(Optional)* If using **Signatrust Enterprise (Self-Hosted)**, update the **Base URL** to your internal endpoint

---

## Usage

### 1. Generate Decision Receipt

Use this operation immediately after an AI decision node.

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

### 2. Verify Decision Receipt

Verify that a receipt has not been tampered with since it was generated.

- **Receipt ID** — The ID returned from Generate

**Returns:**
```json
{
  "receipt_id": "rcpt_a1b2c3d4e5f6",
  "valid": true,
  "agent_name": "LoanApprovalAgent",
  "timestamp": "2026-06-26T11:04:47.265Z",
  "reason": "Signature and hash verified successfully"
}
```

### 3. Get Decision Receipt

Retrieve the full details of a receipt by its ID.

---

## Example Workflow

An example workflow JSON is included in this repository: [`example-workflow.json`](./example-workflow.json)

It demonstrates:
- Calling OpenAI to evaluate a loan application
- Immediately generating a Signatrust receipt for the AI's decision
- Returning both the AI output and the receipt to the caller

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
- **Email**: [partners@signatrust.net](mailto:partners@signatrust.net)
- **Issues**: [GitHub Issues](https://github.com/abokenan444/Signatrust/issues)

---

## License

[MIT](LICENSE) © [Signatrust](https://signatrust.net)
