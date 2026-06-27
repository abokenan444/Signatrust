# langchain-signatrust

**LangChain tools for [Signatrust](https://signatrust.net) — cryptographically signed, tamper-evident AI Decision Receipts.**

[![PyPI](https://img.shields.io/badge/pypi-langchain--signatrust-blue)](https://pypi.org/project/langchain-signatrust/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

Give any LangChain agent the ability to seal its high-stakes decisions into **independently verifiable evidence** — without exposing prompts, model outputs, or sensitive business data. Only SHA-256 hashes are stored by default.

---

## Why?

When an AI agent makes a regulated or high-stakes decision (loan approval, refund, content moderation, transaction flagging), how do you *prove*, after the fact, that the decision was made correctly, under the right policies, and with appropriate human oversight?

Signatrust generates a tamper-evident **AI Decision Receipt** for each decision, capturing:

- Which AI system (model + version) was involved
- The action taken and decision context
- Whether a human reviewed it
- The policies and permissions in effect
- A cryptographic (Ed25519) signature proving the record has not been altered

Each receipt has a public `verify_url` that regulators, auditors, or counterparties can check — without accessing your systems or data.

---

## Installation

```bash
pip install langchain-signatrust
```

## Authentication

Get an API key (starts with `sk_live_…`) from [signatrust.net/register](https://signatrust.net/register), then either pass it explicitly or set an environment variable:

```bash
export SIGNATRUST_API_KEY="sk_live_..."
# Optional, for self-hosted Enterprise:
export SIGNATRUST_BASE_URL="https://signatrust.your-company.com/api/v1"
```

---

## Quick start

```python
from langchain_signatrust import SignatrustGenerateReceiptTool

tool = SignatrustGenerateReceiptTool()  # reads SIGNATRUST_API_KEY from env

receipt = tool.invoke({
    "agent_name": "LoanApprovalAgent",
    "action": "Approved loan application #4821",
    "decision": "APPROVED: applicant meets internal credit policy v3",
    "risk_level": "high",
    "human_review": True,
    "model_provider": "openai",
    "model_name": "gpt-4o",
    "policies": ["eu-ai-act-high-risk", "internal-credit-v3"],
    "permissions": ["credit.decide"],
})

print(receipt["receipt_id"])   # e.g. STR-1A2B3C4D5E
print(receipt["verify_url"])   # https://verify.signatrust.net/r/STR-1A2B3C4D5E
```

## Use with an agent

```python
from langchain_signatrust import get_signatrust_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

tools = get_signatrust_tools()           # all three tools at once
llm = ChatOpenAI(model="gpt-4o")
agent = create_react_agent(llm, tools)

agent.invoke({"messages": [
    ("user", "Approve the refund for order #991 and generate a signed decision receipt.")
]})
```

---

## Tools provided

| Tool | Name | Purpose |
|---|---|---|
| `SignatrustGenerateReceiptTool` | `signatrust_generate_receipt` | Seal an AI decision into a signed receipt |
| `SignatrustVerifyReceiptTool` | `signatrust_verify_receipt` | Verify a receipt's signature/integrity |
| `SignatrustGetReceiptTool` | `signatrust_get_receipt` | Fetch a receipt's full details by ID |

All three tools accept `api_key`, `base_url`, and `timeout` constructor arguments; if omitted, they fall back to the `SIGNATRUST_API_KEY` / `SIGNATRUST_BASE_URL` environment variables.

---

## Privacy-first by design

By default, only the **SHA-256 hash** of the `decision` and `input_prompt` is stored — never the raw text. Pass `include_decision_in_metadata=True` only if you explicitly want to retain the raw decision in the receipt metadata.

---

## Development

```bash
pip install -e ".[test]"
pytest
```

---

## Links

- Website: [signatrust.net](https://signatrust.net)
- API docs: [signatrust.net/docs/api](https://signatrust.net/docs/api)
- Source: [github.com/abokenan444/Signatrust](https://github.com/abokenan444/Signatrust)
- Contact: [partners@signatrust.net](mailto:partners@signatrust.net)

© 2026 Signatrust — MIT License
