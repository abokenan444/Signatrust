"""OpenAI Agents SDK tools for Signatrust — signed AI Decision Receipts.

The OpenAI Agents SDK turns any Python function decorated with ``@function_tool``
into a tool: the schema is built from the function signature, and the
description/argument docs come from the Google-style docstring.

This module exposes three ``FunctionTool`` objects (generate/verify/get) built on
top of the shared :class:`SignatrustClient`, plus a ``get_signatrust_tools``
helper and a ``configure`` function for setting credentials.

Example:
    from agents import Agent
    from openai_agents_signatrust import get_signatrust_tools

    agent = Agent(
        name="ComplianceAgent",
        instructions="Seal high-stakes decisions with a Signatrust receipt.",
        tools=get_signatrust_tools(api_key="sk_live_..."),
    )
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from agents import function_tool

from .client import SignatrustClient

RISK_LEVELS = ("low", "medium", "high", "critical")

_DEFAULT_CLIENT: Optional[SignatrustClient] = None


def configure(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 30,
) -> SignatrustClient:
    """Set the default Signatrust client used by the tool functions."""
    global _DEFAULT_CLIENT
    _DEFAULT_CLIENT = SignatrustClient(api_key=api_key, base_url=base_url, timeout=timeout)
    return _DEFAULT_CLIENT


def _client() -> SignatrustClient:
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = SignatrustClient()  # reads env vars
    return _DEFAULT_CLIENT


@function_tool
def signatrust_generate_receipt(
    agent_name: str,
    action: str,
    decision: str,
    workflow_name: Optional[str] = None,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    model_version: Optional[str] = None,
    decision_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    human_review: Optional[bool] = None,
    policies: Optional[Union[str, List[str]]] = None,
    permissions: Optional[Union[str, List[str]]] = None,
    tags: Optional[Union[str, List[str]]] = None,
    include_decision_in_metadata: bool = False,
) -> Dict[str, Any]:
    """Generate a cryptographically signed, tamper-evident AI Decision Receipt.

    Use this after a high-stakes or regulated AI-assisted decision to create
    independently verifiable evidence. Returns a receipt_id and public verify_url.

    Args:
        agent_name: Display name of the AI agent that made the decision.
        action: Short description of the action the AI agent took.
        decision: The output/result returned by the AI agent. Only its SHA-256 hash is stored by default.
        workflow_name: Optional workflow or team name.
        model_provider: AI provider, e.g. 'openai'.
        model_name: AI model, e.g. 'gpt-4o'.
        model_version: AI model version tag.
        decision_type: Semantic label, e.g. 'refund_approval'.
        risk_level: One of 'low', 'medium', 'high', 'critical'.
        human_review: Whether a human reviewed the decision.
        policies: Governing policies (string or list).
        permissions: Permissions exercised (string or list).
        tags: Tags to categorise this receipt (string or list).
        include_decision_in_metadata: If True, also store the raw decision text.
    """
    if risk_level is not None and risk_level not in RISK_LEVELS:
        raise ValueError(f"risk_level must be one of {RISK_LEVELS}, got {risk_level!r}")
    return _client().generate_receipt(
        agent_name=agent_name,
        action=action,
        decision=decision,
        workflow_name=workflow_name,
        model_provider=model_provider,
        model_name=model_name,
        model_version=model_version,
        decision_type=decision_type,
        risk_level=risk_level,
        human_review=human_review,
        policies=policies,
        permissions=permissions,
        tags=tags,
        include_decision_in_metadata=include_decision_in_metadata,
    )


@function_tool
def signatrust_verify_receipt(receipt_id: str) -> Dict[str, Any]:
    """Verify the authenticity and integrity of an existing Signatrust receipt.

    Args:
        receipt_id: The unique Signatrust receipt ID, e.g. 'STR-1A2B3C4D5E'.
    """
    return _client().verify_receipt(receipt_id)


@function_tool
def signatrust_get_receipt(receipt_id: str) -> Dict[str, Any]:
    """Retrieve the full details of a Signatrust receipt by its ID.

    Args:
        receipt_id: The unique Signatrust receipt ID, e.g. 'STR-1A2B3C4D5E'.
    """
    return _client().get_receipt(receipt_id)


def get_signatrust_tools(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 30,
) -> List[Any]:
    """Return all three Signatrust tools as OpenAI Agents SDK ``FunctionTool`` objects.

    Configures the shared client from the given credentials (or env vars if omitted).
    """
    configure(api_key=api_key, base_url=base_url, timeout=timeout)
    return [
        signatrust_generate_receipt,
        signatrust_verify_receipt,
        signatrust_get_receipt,
    ]
