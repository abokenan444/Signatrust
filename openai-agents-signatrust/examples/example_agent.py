"""Example: an OpenAI Agents SDK agent that signs its decisions with Signatrust.

Run:
    export SIGNATRUST_API_KEY="sk_live_..."
    export OPENAI_API_KEY="sk-..."
    python example_agent.py
"""

from openai_agents_signatrust import configure, signatrust_generate_receipt


def standalone_example() -> None:
    """Call the underlying client directly (no LLM), via the shared client."""
    client = configure()  # reads SIGNATRUST_API_KEY from env
    receipt = client.generate_receipt(
        agent_name="RefundAgent",
        action="Approved refund for order #991",
        decision="APPROVED: order qualifies under the 30-day return policy",
        decision_type="refund_approval",
        risk_level="medium",
        human_review=False,
        model_provider="openai",
        model_name="gpt-4o",
        policies=["refunds-v2"],
        permissions=["refunds.approve"],
        tags=["ecommerce", "refund"],
    )
    print("Receipt ID :", receipt.get("receipt_id"))
    print("Verify URL :", receipt.get("verify_url"))


def agent_example() -> None:
    """Wire the tools into an OpenAI Agents SDK agent (requires OPENAI_API_KEY)."""
    from agents import Agent, Runner

    from openai_agents_signatrust import get_signatrust_tools

    agent = Agent(
        name="ComplianceAgent",
        instructions=(
            "You approve refunds. After every decision you MUST call "
            "signatrust_generate_receipt to produce a signed, verifiable receipt, "
            "then report the verify_url."
        ),
        tools=get_signatrust_tools(),
    )

    result = Runner.run_sync(
        agent,
        "Approve the refund for order #991 (within the 30-day policy) and seal a Signatrust receipt.",
    )
    print(result.final_output)


if __name__ == "__main__":
    standalone_example()
    # agent_example()  # uncomment if OPENAI_API_KEY is configured
