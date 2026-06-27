"""Example: an AutoGen agent that signs its decisions with Signatrust.

Run:
    export SIGNATRUST_API_KEY="sk_live_..."
    export OPENAI_API_KEY="sk-..."
    python example_agent.py
"""

import asyncio

from autogen_core import CancellationToken

from autogen_signatrust import get_signatrust_tools


async def standalone_example() -> None:
    """Call the generate tool directly, without an LLM."""
    generate_tool = get_signatrust_tools()[0]  # reads SIGNATRUST_API_KEY from env
    result = await generate_tool.run_json(
        {
            "agent_name": "RefundAgent",
            "action": "Approved refund for order #991",
            "decision": "APPROVED: order qualifies under the 30-day return policy",
            "decision_type": "refund_approval",
            "risk_level": "medium",
            "human_review": False,
            "model_provider": "openai",
            "model_name": "gpt-4o",
            "policies": ["refunds-v2"],
            "permissions": ["refunds.approve"],
            "tags": ["ecommerce", "refund"],
        },
        CancellationToken(),
    )
    print("Receipt:", result)


async def agent_example() -> None:
    """Wire the tools into an AutoGen AssistantAgent (requires an LLM provider key)."""
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    model_client = OpenAIChatCompletionClient(model="gpt-4o")
    agent = AssistantAgent(
        name="compliance_agent",
        model_client=model_client,
        tools=get_signatrust_tools(),
        system_message=(
            "You approve refunds. After every decision, you MUST call "
            "signatrust_generate_receipt to produce a signed, verifiable receipt, "
            "then report the verify_url."
        ),
    )
    result = await agent.run(
        task="Approve the refund for order #991 (within the 30-day policy) and seal a Signatrust receipt."
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(standalone_example())
    # asyncio.run(agent_example())  # uncomment if an LLM provider key is configured
