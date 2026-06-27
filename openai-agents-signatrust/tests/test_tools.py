"""Unit tests for openai-agents-signatrust tools (HTTP API mocked).

The OpenAI Agents SDK wraps functions into FunctionTool objects whose callable is
``on_invoke_tool(ctx, args_json)``. We invoke that directly to exercise the full
schema-parse + dispatch path.
"""

import asyncio
import json

import pytest
import requests_mock
from agents.tool_context import ToolContext
from agents.usage import Usage

from openai_agents_signatrust import (
    configure,
    get_signatrust_tools,
    signatrust_generate_receipt,
    signatrust_get_receipt,
    signatrust_verify_receipt,
)

BASE = "https://signatrust.net/api/v1"
API_KEY = "sk_live_test_key"


@pytest.fixture(autouse=True)
def _configure():
    configure(api_key=API_KEY)


def _invoke(tool, **kwargs):
    """Invoke an Agents SDK FunctionTool by calling its on_invoke_tool with JSON args."""
    ctx = ToolContext(
        context=None,
        usage=Usage(),
        tool_name=tool.name,
        tool_call_id="call_test",
        tool_arguments=json.dumps(kwargs),
    )
    return asyncio.new_event_loop().run_until_complete(
        tool.on_invoke_tool(ctx, json.dumps(kwargs))
    )


def test_tools_are_function_tools():
    tools = get_signatrust_tools(api_key=API_KEY)
    assert len(tools) == 3
    names = {t.name for t in tools}
    assert names == {
        "signatrust_generate_receipt",
        "signatrust_verify_receipt",
        "signatrust_get_receipt",
    }
    # each tool exposes a JSON schema generated from the signature
    for t in tools:
        assert t.params_json_schema is not None


def test_generate_receipt_sends_correct_body():
    with requests_mock.Mocker() as m:
        m.post(
            f"{BASE}/receipts",
            json={"receipt_id": "STR-XYZ789", "verify_url": "https://verify.signatrust.net/r/STR-XYZ789"},
            status_code=201,
        )
        out = _invoke(
            signatrust_generate_receipt,
            agent_name="LoanApprovalAgent",
            action="Approved loan application",
            decision="APPROVED",
            risk_level="high",
            human_review=True,
            policies=["eu-ai-act-high-risk", "internal-credit-v3"],
            model_provider="openai",
            model_name="gpt-4o",
        )
        assert "STR-XYZ789" in str(out)
        sent = m.last_request.json()
        assert sent["agent_name"] == "LoanApprovalAgent"
        assert sent["risk_level"] == "high"
        assert sent["human_review"] is True
        assert sent["policies"] == "eu-ai-act-high-risk,internal-credit-v3"
        assert sent["model"]["name"] == "gpt-4o"
        assert m.last_request.headers["X-API-Key"] == API_KEY


def test_generate_receipt_rejects_bad_risk_level():
    out = _invoke(
        signatrust_generate_receipt,
        agent_name="A",
        action="x",
        decision="y",
        risk_level="ultra-mega",
    )
    # The SDK captures tool exceptions and returns an error string by default
    assert "risk_level" in str(out) or "error" in str(out).lower()


def test_verify_receipt():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/STR-XYZ789/verify", json={"valid": True})
        out = _invoke(signatrust_verify_receipt, receipt_id="STR-XYZ789")
        assert "true" in str(out).lower() or "valid" in str(out).lower()


def test_get_receipt():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/STR-XYZ789", json={"receipt_id": "STR-XYZ789"})
        out = _invoke(signatrust_get_receipt, receipt_id="STR-XYZ789")
        assert "STR-XYZ789" in str(out)
