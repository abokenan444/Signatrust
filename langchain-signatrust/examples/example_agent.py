"""Example: a LangChain agent that signs its decisions with Signatrust.

Run:
    export SIGNATRUST_API_KEY="sk_live_..."
    export OPENAI_API_KEY="sk-..."
    python example_agent.py
"""

from langchain_signatrust import (
    SignatrustGenerateReceiptTool,
    get_signatrust_tools,
)


def standalone_example() -> None:
    """Generate a receipt directly, without an LLM."""
    tool = SignatrustGenerateReceiptTool()  # reads SIGNATRUST_API_KEY from env
    receipt = tool.invoke(
        {
            "agent_name": "RefundAgent",
            "action": "Approved refund for order #991",
            "decision": "APPROVED: order qualifies under 30-day return policy",
            "decision_type": "refund_approval",
            "risk_level": "medium",
            "human_review": False,
            "model_provider": "openai",
            "model_name": "gpt-4o",
            "policies": ["refunds-v2"],
            "permissions": ["refunds.approve"],
            "tags": ["ecommerce", "refund"],
        }
    )
    print("Receipt ID :", receipt.get("receipt_id"))
    print("Verify URL :", receipt.get("verify_url"))


def agent_example() -> None:
    """Wire the tools into a ReAct agent (requires langchain-openai + langgraph)."""
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    tools = get_signatrust_tools()
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    agent = create_react_agent(llm, tools)

    result = agent.invoke(
        {
            "messages": [
                (
                    "user",
                    "You are a refund agent. Approve the refund for order #991 "
                    "(within the 30-day policy), then generate a signed Signatrust "
                    "decision receipt for the approval and report the verify URL.",
                )
            ]
        }
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    standalone_example()
    # agent_example()  # uncomment if langchain-openai + langgraph are installed
