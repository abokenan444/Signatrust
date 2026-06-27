"""Unit tests for autogen-signatrust tools (HTTP API mocked)."""

import pytest
import requests_mock

from autogen_signatrust import (
    configure,
    signatrust_generate_receipt,
    signatrust_get_receipt,
    signatrust_verify_receipt,
)
from autogen_signatrust.client import SignatrustError

BASE = "https://signatrust.net/api/v1"
API_KEY = "sk_live_test_key"


@pytest.fixture(autouse=True)
def _configure():
    configure(api_key=API_KEY)


@pytest.mark.asyncio
async def test_generate_receipt_sends_correct_body():
    with requests_mock.Mocker() as m:
        m.post(
            f"{BASE}/receipts",
            json={"receipt_id": "STR-ABC123", "verify_url": "https://verify.signatrust.net/r/STR-ABC123"},
            status_code=201,
        )
        result = await signatrust_generate_receipt(
            agent_name="LoanApprovalAgent",
            action="Approved loan application",
            decision="APPROVED",
            risk_level="high",
            human_review=True,
            policies=["eu-ai-act-high-risk", "internal-credit-v3"],
            model_provider="openai",
            model_name="gpt-4o",
        )
        assert result["receipt_id"] == "STR-ABC123"
        sent = m.last_request.json()
        assert sent["agent_name"] == "LoanApprovalAgent"
        assert sent["risk_level"] == "high"
        assert sent["human_review"] is True
        assert sent["policies"] == "eu-ai-act-high-risk,internal-credit-v3"
        assert sent["model"]["name"] == "gpt-4o"
        assert m.last_request.headers["X-API-Key"] == API_KEY


@pytest.mark.asyncio
async def test_generate_receipt_rejects_bad_risk_level():
    with pytest.raises(ValueError):
        await signatrust_generate_receipt(
            agent_name="A", action="x", decision="y", risk_level="ultra-mega"
        )


@pytest.mark.asyncio
async def test_verify_receipt():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/STR-ABC123/verify", json={"valid": True})
        result = await signatrust_verify_receipt("STR-ABC123")
        assert result["valid"] is True


@pytest.mark.asyncio
async def test_get_receipt():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/STR-ABC123", json={"receipt_id": "STR-ABC123"})
        result = await signatrust_get_receipt("STR-ABC123")
        assert result["receipt_id"] == "STR-ABC123"


@pytest.mark.asyncio
async def test_api_error_raises():
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/BAD", status_code=404, json={"error": "not found"})
        with pytest.raises(SignatrustError):
            await signatrust_get_receipt("BAD")


def test_function_tool_wrapping():
    """get_signatrust_tools should produce 3 AutoGen FunctionTool objects."""
    from autogen_signatrust import get_signatrust_tools

    tools = get_signatrust_tools(api_key=API_KEY)
    assert len(tools) == 3
    names = {t.name for t in tools}
    assert names == {
        "signatrust_generate_receipt",
        "signatrust_verify_receipt",
        "signatrust_get_receipt",
    }
    # each tool exposes a JSON schema
    for t in tools:
        assert t.schema["name"]
