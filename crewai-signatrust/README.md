# crewai-signatrust

**CrewAI tools for [Signatrust](https://signatrust.net) — cryptographically signed, tamper-evident AI Decision Receipts.**

[![PyPI](https://img.shields.io/badge/pypi-crewai--signatrust-blue)](https://pypi.org/project/crewai-signatrust/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

Give any CrewAI agent the ability to seal its high-stakes decisions into **independently verifiable evidence** — without exposing prompts, model outputs, or sensitive business data. Only SHA-256 hashes are stored by default.

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
pip install crewai-signatrust
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
from crewai import Agent, Task, Crew
from crewai_signatrust import get_signatrust_tools

compliance_officer = Agent(
    role="Compliance Officer",
    goal="Approve refunds and produce verifiable Signatrust decision receipts",
    backstory="You ensure every AI-assisted decision is auditable and signed.",
    tools=get_signatrust_tools(),  # reads SIGNATRUST_API_KEY from env
)

task = Task(
    description=(
        "Approve the refund for order #991 (within the 30-day policy), then "
        "generate a signed Signatrust decision receipt and report the verify URL."
    ),
    expected_output="The receipt_id and public verify_url of the signed decision.",
    agent=compliance_officer,
)

crew = Crew(agents=[compliance_officer], tasks=[task])
print(crew.kickoff())
```

## Direct (non-agent) use

```python
from crewai_signatrust import SignatrustGenerateReceiptTool

tool = SignatrustGenerateReceiptTool()
receipt = tool.run(
    agent_name="RefundAgent",
    action="Approved refund for order #991",
    decision="APPROVED: order qualifies under 30-day return policy",
    risk_level="medium",
    human_review=False,
    policies=["refunds-v2"],
)
print(receipt["receipt_id"], receipt["verify_url"])
```

---

## Tools provided

| Tool | Name | Purpose |
|---|---|---|
| `SignatrustGenerateReceiptTool` | `Signatrust Generate Decision Receipt` | Seal an AI decision into a signed receipt |
| `SignatrustVerifyReceiptTool` | `Signatrust Verify Decision Receipt` | Verify a receipt's signature/integrity |
| `SignatrustGetReceiptTool` | `Signatrust Get Decision Receipt` | Fetch a receipt's full details by ID |

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
