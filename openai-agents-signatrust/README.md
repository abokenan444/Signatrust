# openai-agents-signatrust

**[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) tools for [Signatrust](https://signatrust.net) — cryptographically signed, tamper-evident AI Decision Receipts.**

[![PyPI](https://img.shields.io/badge/pypi-openai--agents--signatrust-blue)](https://pypi.org/project/openai-agents-signatrust/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

Give any OpenAI Agents SDK agent the ability to seal its high-stakes decisions into **independently verifiable evidence** — without exposing prompts, model outputs, or sensitive business data. Only SHA-256 hashes are stored by default.

---

## Why?

When an AI agent makes a regulated or high-stakes decision (loan approval, refund, content moderation, transaction flagging), how do you *prove*, after the fact, that the decision was made correctly, under the right policies, and with appropriate human oversight?

Signatrust generates a tamper-evident **AI Decision Receipt** for each decision, capturing which AI system was involved, the action taken, whether a human reviewed it, the policies/permissions in effect, and a cryptographic (Ed25519) signature. Each receipt has a public `verify_url` that regulators, auditors, or counterparties can check — without accessing your systems or data.

---

## Installation

```bash
pip install openai-agents-signatrust
```

## Authentication

```bash
export SIGNATRUST_API_KEY="sk_live_..."
# Optional, for self-hosted Enterprise:
export SIGNATRUST_BASE_URL="https://signatrust.your-company.com/api/v1"
```

---

## Quick start

```python
from agents import Agent, Runner
from openai_agents_signatrust import get_signatrust_tools

agent = Agent(
    name="ComplianceAgent",
    instructions=(
        "You approve refunds. After every decision you MUST call "
        "signatrust_generate_receipt to produce a signed, verifiable receipt, "
        "then report the verify_url."
    ),
    tools=get_signatrust_tools(),   # reads SIGNATRUST_API_KEY from env
)

result = Runner.run_sync(
    agent,
    "Approve the refund for order #991 (within the 30-day policy) and seal a Signatrust receipt.",
)
print(result.final_output)
```

You can also import the decorated tools individually:

```python
from openai_agents_signatrust import (
    signatrust_generate_receipt,
    signatrust_verify_receipt,
    signatrust_get_receipt,
    configure,
)

configure(api_key="sk_live_...")   # or rely on SIGNATRUST_API_KEY
agent = Agent(name="...", tools=[signatrust_generate_receipt])
```

---

## Tools provided

| Tool | Purpose |
|---|---|
| `signatrust_generate_receipt` | Seal an AI decision into a signed receipt |
| `signatrust_verify_receipt` | Verify a receipt's signature/integrity |
| `signatrust_get_receipt` | Fetch a receipt's full details by ID |

These are standard OpenAI Agents SDK `FunctionTool` objects produced by the `@function_tool` decorator — the JSON schema is generated automatically from each function's signature and Google-style docstring.

---

## Privacy-first by design

By default, only the **SHA-256 hash** of the `decision` and `input_prompt` is stored — never the raw text. Pass `include_decision_in_metadata=True` only if you explicitly want to retain the raw decision.

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
