"""AutoGen tools for Signatrust — cryptographically signed AI Decision Receipts.

AutoGen wraps plain Python functions in ``autogen_core.tools.FunctionTool``,
using type annotations and the description to build the JSON schema sent to the
model. This module exposes three async functions (generate/verify/get) plus a
helper that returns ready-to-use ``FunctionTool`` instances.

Example:
    from autogen_signatrust import get_signatrust_tools

    tools = get_signatrust_tools(api_key="sk_live_...")
    # pass `tools` to an AutoGen AssistantAgent or model_client.create(...)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from typing_extensions import Annotated

from .client import SignatrustClient

RISK_LEVELS = ("low", "medium", "high", "critical")

# Module-level configuration used by the bare functions. ``configure`` or
# ``get_signatrust_tools`` set this; falls back to env vars otherwise.
_DEFAULT_CLIENT: Optional[SignatrustClient] = None


def configure(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 30,
) -> SignatrustClient:
    """Set the default Signatrust client used by the module-level tool functions."""
    global _DEFAULT_CLIENT
    _DEFAULT_CLIENT = SignatrustClient(api_key=api_key, base_url=base_url, timeout=timeout)
    return _DEFAULT_CLIENT


def _client() -> SignatrustClient:
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = SignatrustClient()  # reads env vars
    return _DEFAULT_CLIENT


async def signatrust_generate_receipt(
    agent_name: Annotated[str, "Display name of the AI agent that made the decision."],
    action: Annotated[str, "Short description of the action the AI agent took."],
    decision: Annotated[str, "The output/result returned by the AI agent. Only its SHA-256 hash is stored by default."],
    workflow_name: Annotated[Optional[str], "Optional workflow/team name."] = None,
    model_provider: Annotated[Optional[str], "AI provider, e.g. 'openai'."] = None,
    model_name: Annotated[Optional[str], "AI model, e.g. 'gpt-4o'."] = None,
    model_version: Annotated[Optional[str], "AI model version tag."] = None,
    decision_type: Annotated[Optional[str], "Semantic label, e.g. 'refund_approval'."] = None,
    risk_level: Annotated[Optional[str], "One of 'low','medium','high','critical'."] = None,
    human_review: Annotated[Optional[bool], "Whether a human reviewed the decision."] = None,
    policies: Annotated[Optional[Union[str, List[str]]], "Governing policies."] = None,
    permissions: Annotated[Optional[Union[str, List[str]]], "Permissions exercised."] = None,
    tags: Annotated[Optional[Union[str, List[str]]], "Tags to categorise this receipt."] = None,
    include_decision_in_metadata: Annotated[bool, "If True, also store the raw decision text."] = False,
) -> Dict[str, Any]:
    """Generate a cryptographically signed, tamper-evident AI Decision Receipt.

    Use this after a high-stakes or regulated AI-assisted decision to create
    independently verifiable evidence. Returns a receipt_id and a public verify_url.
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


async def signatrust_verify_receipt(
    receipt_id: Annotated[str, "The unique Signatrust receipt ID, e.g. 'STR-1A2B3C4D5E'."],
) -> Dict[str, Any]:
    """Verify the authenticity and integrity of an existing Signatrust receipt by ID."""
    return _client().verify_receipt(receipt_id)


async def signatrust_get_receipt(
    receipt_id: Annotated[str, "The unique Signatrust receipt ID, e.g. 'STR-1A2B3C4D5E'."],
) -> Dict[str, Any]:
    """Retrieve the full details of a Signatrust receipt by its ID."""
    return _client().get_receipt(receipt_id)


def get_signatrust_tools(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 30,
) -> List[Any]:
    """Return all three Signatrust tools wrapped as AutoGen ``FunctionTool`` objects.

    Requires the ``autogen-core`` package. Configures the shared client from the
    given credentials (or env vars if omitted).
    """
    from autogen_core.tools import FunctionTool

    configure(api_key=api_key, base_url=base_url, timeout=timeout)
    return [
        FunctionTool(
            signatrust_generate_receipt,
            description="Generate a cryptographically signed, tamper-evident AI Decision Receipt.",
        ),
        FunctionTool(
            signatrust_verify_receipt,
            description="Verify the authenticity and integrity of an existing Signatrust receipt.",
        ),
        FunctionTool(
            signatrust_get_receipt,
            description="Retrieve the full details of a Signatrust receipt by its ID.",
        ),
    ]
