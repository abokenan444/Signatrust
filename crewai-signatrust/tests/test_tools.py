"""Unit tests for crewai-signatrust tools (HTTP API mocked)."""

import pytest
import requests_mock

from crewai_signatrust import (
    SignatrustGenerateReceiptTool,
    SignatrustGetReceiptTool,
    SignatrustVerifyReceiptTool,
    get_signatrust_tools,
)
from crewai_signatrust.client import SignatrustError

BASE = "https://signatrust.net/api/v1"
API_KEY = "sk_live_test_key"


def test_generate_receipt_sends_correct_body():
    tool = SignatrustGenerateReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.post(
            f"{BASE}/receipts",
            json={"receipt_id": "STR-ABC123", "verify_url": "https://verify.signatrust.net/r/STR-ABC123"},
            status_code=201,
        )
        result = tool.run(
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


def test_generate_receipt_rejects_bad_risk_level():
    tool = SignatrustGenerateReceiptTool(api_key=API_KEY)
    with pytest.raises(Exception):
        tool.run(
            agent_name="A",
            action="x",
            decision="y",
            risk_level="ultra-mega",
        )


def test_verify_receipt():
    tool = SignatrustVerifyReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/STR-ABC123/verify", json={"valid": True})
        result = tool.run(receipt_id="STR-ABC123")
        assert result["valid"] is True


def test_get_receipt():
    tool = SignatrustGetReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/STR-ABC123", json={"receipt_id": "STR-ABC123"})
        result = tool.run(receipt_id="STR-ABC123")
        assert result["receipt_id"] == "STR-ABC123"


def test_api_error_raises():
    tool = SignatrustGetReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/BAD", status_code=404, json={"error": "not found"})
        with pytest.raises(SignatrustError):
            tool.run(receipt_id="BAD")


def test_tool_metadata():
    gen = SignatrustGenerateReceiptTool(api_key=API_KEY)
    assert gen.name == "Signatrust Generate Decision Receipt"
    assert gen.description
    schema = gen.args_schema.model_json_schema()
    assert "agent_name" in schema["properties"]


def test_get_signatrust_tools_helper():
    tools = get_signatrust_tools(api_key=API_KEY)
    assert len(tools) == 3
    names = {t.name for t in tools}
    assert names == {
        "Signatrust Generate Decision Receipt",
        "Signatrust Verify Decision Receipt",
        "Signatrust Get Decision Receipt",
    }
