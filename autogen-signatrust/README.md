# autogen-signatrust

**AutoGen tools for [Signatrust](https://signatrust.net) — cryptographically signed, tamper-evident AI Decision Receipts.**

[![PyPI](https://img.shields.io/badge/pypi-autogen--signatrust-blue)](https://pypi.org/project/autogen-signatrust/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

Give any [AutoGen](https://microsoft.github.io/autogen/) agent the ability to seal its high-stakes decisions into **independently verifiable evidence** — without exposing prompts, model outputs, or sensitive business data. Only SHA-256 hashes are stored by default.

---

## Why?

When an AI agent makes a regulated or high-stakes decision (loan approval, refund, content moderation, transaction flagging), how do you *prove*, after the fact, that the decision was made correctly, under the right policies, and with appropriate human oversight?

Signatrust generates a tamper-evident **AI Decision Receipt** for each decision, capturing which AI system was involved, the action taken, whether a human reviewed it, the policies/permissions in effect, and a cryptographic (Ed25519) signature. Each receipt has a public `verify_url` that regulators, auditors, or counterparties can check — without accessing your systems or data.

---

## Installation

```bash
pip install autogen-signatrust
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
from autogen_signatrust import get_signatrust_tools

# Returns three autogen_core.tools.FunctionTool objects
tools = get_signatrust_tools()   # reads SIGNATRUST_API_KEY from env
```

### Use with an AutoGen AssistantAgent (AgentChat)

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_signatrust import get_signatrust_tools

model_client = OpenAIChatCompletionClient(model="gpt-4o")
agent = AssistantAgent(
    name="compliance_agent",
    model_client=model_client,
    tools=get_signatrust_tools(),
    system_message="After any high-stakes decision, generate a signed Signatrust receipt.",
)
```

### Use a single tool directly

```python
import asyncio
from autogen_core import CancellationToken
from autogen_signatrust import get_signatrust_tools

generate_tool = get_signatrust_tools()[0]

async def main():
    result = await generate_tool.run_json(
        {
            "agent_name": "RefundAgent",
            "action": "Approved refund for order #991",
            "decision": "APPROVED under 30-day return policy",
            "risk_level": "medium",
        },
        CancellationToken(),
    )
    print(result)

asyncio.run(main())
```

---

## Tools provided

| Function | Tool name | Purpose |
|---|---|---|
| `signatrust_generate_receipt` | `signatrust_generate_receipt` | Seal an AI decision into a signed receipt |
| `signatrust_verify_receipt` | `signatrust_verify_receipt` | Verify a receipt's signature/integrity |
| `signatrust_get_receipt` | `signatrust_get_receipt` | Fetch a receipt's full details by ID |

The bare async functions can also be imported directly and wrapped manually with `autogen_core.tools.FunctionTool`. Use `configure(api_key=..., base_url=...)` to set credentials for the bare functions, or rely on environment variables.

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
