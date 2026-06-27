"""Example: a CrewAI agent that signs its decisions with Signatrust.

Run:
    export SIGNATRUST_API_KEY="sk_live_..."
    export OPENAI_API_KEY="sk-..."
    python example_crew.py
"""

from crewai_signatrust import SignatrustGenerateReceiptTool


def standalone_example() -> None:
    """Generate a receipt directly, without an LLM."""
    tool = SignatrustGenerateReceiptTool()  # reads SIGNATRUST_API_KEY from env
    receipt = tool.run(
        agent_name="RefundAgent",
        action="Approved refund for order #991",
        decision="APPROVED: order qualifies under 30-day return policy",
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


def crew_example() -> None:
    """Wire the tools into a CrewAI crew (requires an LLM provider key)."""
    from crewai import Agent, Crew, Task
    from crewai_signatrust import get_signatrust_tools

    compliance_officer = Agent(
        role="Compliance Officer",
        goal="Approve refunds and produce verifiable Signatrust decision receipts",
        backstory="You ensure every AI-assisted decision is auditable and signed.",
        tools=get_signatrust_tools(),
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


if __name__ == "__main__":
    standalone_example()
    # crew_example()  # uncomment if an LLM provider key is configured
