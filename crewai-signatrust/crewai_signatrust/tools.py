"""CrewAI tools for Signatrust — cryptographically signed AI Decision Receipts.

These tools let a CrewAI agent generate, verify, and retrieve tamper-evident
AI Decision Receipts via the Signatrust API, producing independently verifiable
evidence of high-stakes decisions — without exposing prompts, model outputs, or
sensitive business data (only SHA-256 hashes are stored by default).

Example:
    from crewai import Agent
    from crewai_signatrust import SignatrustGenerateReceiptTool

    agent = Agent(
        role="Compliance Officer",
        goal="Approve refunds and produce verifiable decision receipts",
        tools=[SignatrustGenerateReceiptTool(api_key="sk_live_...")],
    )
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from .client import SignatrustClient

RISK_LEVELS = ("low", "medium", "high", "critical")


# ─── Input schemas ───────────────────────────────────────────────────────────
class GenerateReceiptInput(BaseModel):
    """Input schema for generating a Signatrust AI Decision Receipt."""

    agent_name: str = Field(
        description="Display name of the AI agent that made the decision, e.g. 'LoanApprovalAgent'."
    )
    action: str = Field(
        description="Short description of the action taken, e.g. 'Approved loan application'."
    )
    decision: str = Field(
        description=(
            "The output or result returned by the AI agent. Only its SHA-256 hash "
            "is stored unless raw retention is enabled."
        )
    )
    workflow_name: Optional[str] = Field(
        default=None, description="Optional name of the workflow/crew in which the decision was made."
    )
    model_provider: Optional[str] = Field(
        default=None, description="AI provider, e.g. 'openai', 'anthropic'."
    )
    model_name: Optional[str] = Field(default=None, description="AI model, e.g. 'gpt-4o'.")
    model_version: Optional[str] = Field(
        default=None, description="Version tag of the AI model, e.g. '2025-08-01'."
    )
    decision_type: Optional[str] = Field(
        default=None, description="Semantic label, e.g. 'loan_decision', 'refund_approval'."
    )
    risk_level: Optional[str] = Field(
        default=None, description="One of 'low', 'medium', 'high', 'critical'."
    )
    human_review: Optional[bool] = Field(
        default=None, description="Whether a human reviewed the decision before it was finalised."
    )
    policies: Optional[Union[str, List[str]]] = Field(
        default=None, description="Governing policies, e.g. ['eu-ai-act-high-risk']."
    )
    permissions: Optional[Union[str, List[str]]] = Field(
        default=None, description="Permissions exercised, e.g. ['credit.decide']."
    )
    tags: Optional[Union[str, List[str]]] = Field(
        default=None, description="Tags to categorise this receipt."
    )
    include_decision_in_metadata: bool = Field(
        default=False,
        description="If True, also store the raw decision text (off by default; privacy-first).",
    )


class ReceiptIdInput(BaseModel):
    """Input schema for verifying or fetching a receipt by its id."""

    receipt_id: str = Field(description="The unique Signatrust receipt ID, e.g. 'STR-1A2B3C4D5E'.")


# ─── Output schemas (typed outputs help the agent read structured fields) ─────
class ReceiptOutput(BaseModel):
    """Structured output for a generated/fetched receipt."""

    receipt_id: Optional[str] = Field(default=None, description="The unique receipt ID.")
    verify_url: Optional[str] = Field(default=None, description="Public verification URL.")
    signature: Optional[str] = Field(default=None, description="Cryptographic signature.")
    hash: Optional[str] = Field(default=None, description="SHA-256 hash of the decision.")


# ─── Tools ───────────────────────────────────────────────────────────────────
class _SignatrustToolBase(BaseTool):
    """Shared base that lazily constructs a SignatrustClient."""

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30

    _client: Optional[SignatrustClient] = PrivateAttr(default=None)

    def _get_client(self) -> SignatrustClient:
        if self._client is None:
            self._client = SignatrustClient(
                api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
            )
        return self._client


class SignatrustGenerateReceiptTool(_SignatrustToolBase):
    """Generate a cryptographically signed AI Decision Receipt with Signatrust."""

    name: str = "Signatrust Generate Decision Receipt"
    description: str = (
        "Generate a cryptographically signed, tamper-evident AI Decision Receipt for an "
        "AI-assisted decision. Records which AI system was involved, the action taken, "
        "policies/permissions in effect, and whether a human reviewed it. Returns a "
        "receipt_id and a public verify_url. Use after a high-stakes or regulated decision "
        "to create independently verifiable evidence."
    )
    args_schema: Type[BaseModel] = GenerateReceiptInput

    def _run(
        self,
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
        if risk_level is not None and risk_level not in RISK_LEVELS:
            raise ValueError(f"risk_level must be one of {RISK_LEVELS}, got {risk_level!r}")
        return self._get_client().generate_receipt(
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


class SignatrustVerifyReceiptTool(_SignatrustToolBase):
    """Verify the authenticity and integrity of an existing Signatrust receipt."""

    name: str = "Signatrust Verify Decision Receipt"
    description: str = (
        "Verify the authenticity and integrity of an existing Signatrust AI Decision "
        "Receipt by its ID. Returns whether the cryptographic signature is valid and the "
        "record has not been altered."
    )
    args_schema: Type[BaseModel] = ReceiptIdInput

    def _run(self, receipt_id: str) -> Dict[str, Any]:
        return self._get_client().verify_receipt(receipt_id)


class SignatrustGetReceiptTool(_SignatrustToolBase):
    """Retrieve the full details of a Signatrust receipt by its id."""

    name: str = "Signatrust Get Decision Receipt"
    description: str = (
        "Retrieve the full details of a Signatrust AI Decision Receipt by its ID, "
        "including metadata, signature, hash, and verification URL."
    )
    args_schema: Type[BaseModel] = ReceiptIdInput

    def _run(self, receipt_id: str) -> Dict[str, Any]:
        return self._get_client().get_receipt(receipt_id)


def get_signatrust_tools(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 30,
) -> List[BaseTool]:
    """Return all three Signatrust tools, ready to add to a CrewAI agent."""
    kwargs = {"api_key": api_key, "base_url": base_url, "timeout": timeout}
    return [
        SignatrustGenerateReceiptTool(**kwargs),
        SignatrustVerifyReceiptTool(**kwargs),
        SignatrustGetReceiptTool(**kwargs),
    ]
