"""Unit tests for langchain-signatrust tools.

These tests mock the Signatrust HTTP API so they run offline and deterministically.
"""

import pytest
import requests_mock

from langchain_signatrust import (
    SignatrustGenerateReceiptTool,
    SignatrustGetReceiptTool,
    SignatrustVerifyReceiptTool,
    get_signatrust_tools,
)
from langchain_signatrust.client import SignatrustClient, SignatrustError

BASE = "https://signatrust.net/api/v1"
API_KEY = "sk_live_test_key"


# ─── client ──────────────────────────────────────────────────────────────────
def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("SIGNATRUST_API_KEY", raising=False)
    with pytest.raises(ValueError):
        SignatrustClient()


def test_client_reads_env_key(monkeypatch):
    monkeypatch.setenv("SIGNATRUST_API_KEY", "sk_live_env")
    client = SignatrustClient()
    assert client.api_key == "sk_live_env"
    assert client.base_url == BASE


def test_generate_receipt_sends_correct_body():
    tool = SignatrustGenerateReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.post(
            f"{BASE}/receipts",
            json={"receipt_id": "STR-ABC123", "verify_url": "https://verify.signatrust.net/r/STR-ABC123"},
            status_code=201,
        )
        result = tool.invoke(
            {
                "agent_name": "LoanApprovalAgent",
                "action": "Approved loan application",
                "decision": "APPROVED",
                "risk_level": "high",
                "human_review": True,
                "policies": ["eu-ai-act-high-risk", "internal-credit-v3"],
                "model_provider": "openai",
                "model_name": "gpt-4o",
            }
        )
        assert result["receipt_id"] == "STR-ABC123"
        sent = m.last_request.json()
        assert sent["agent_name"] == "LoanApprovalAgent"
        assert sent["risk_level"] == "high"
        assert sent["human_review"] is True
        # list policies should be normalised to comma-separated string
        assert sent["policies"] == "eu-ai-act-high-risk,internal-credit-v3"
        assert sent["model"]["provider"] == "openai"
        assert sent["model"]["name"] == "gpt-4o"
        # X-API-Key header set
        assert m.last_request.headers["X-API-Key"] == API_KEY


def test_generate_receipt_rejects_bad_risk_level():
    tool = SignatrustGenerateReceiptTool(api_key=API_KEY)
    with pytest.raises(Exception):
        tool.invoke(
            {
                "agent_name": "A",
                "action": "x",
                "decision": "y",
                "risk_level": "ultra-mega",
            }
        )


def test_verify_receipt():
    tool = SignatrustVerifyReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.get(
            f"{BASE}/receipts/STR-ABC123/verify",
            json={"valid": True, "receipt_id": "STR-ABC123"},
        )
        result = tool.invoke({"receipt_id": "STR-ABC123"})
        assert result["valid"] is True


def test_get_receipt():
    tool = SignatrustGetReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.get(
            f"{BASE}/receipts/STR-ABC123",
            json={"receipt_id": "STR-ABC123", "agent_name": "LoanApprovalAgent"},
        )
        result = tool.invoke({"receipt_id": "STR-ABC123"})
        assert result["agent_name"] == "LoanApprovalAgent"


def test_api_error_raises():
    tool = SignatrustGetReceiptTool(api_key=API_KEY)
    with requests_mock.Mocker() as m:
        m.get(f"{BASE}/receipts/BAD", status_code=404, json={"error": "not found"})
        with pytest.raises(SignatrustError):
            tool.invoke({"receipt_id": "BAD"})


# ─── tool metadata / schema ────────────────────────────────────────────────
def test_tool_names_and_schema():
    gen = SignatrustGenerateReceiptTool(api_key=API_KEY)
    assert gen.name == "signatrust_generate_receipt"
    assert gen.description
    schema = gen.args_schema.model_json_schema()
    assert "agent_name" in schema["properties"]
    assert "decision" in schema["properties"]


def test_get_signatrust_tools_helper():
    tools = get_signatrust_tools(api_key=API_KEY)
    assert len(tools) == 3
    names = {t.name for t in tools}
    assert names == {
        "signatrust_generate_receipt",
        "signatrust_verify_receipt",
        "signatrust_get_receipt",
    }
