"""LangChain tools for Signatrust — cryptographically signed AI Decision Receipts.

These tools let a LangChain agent generate, verify, and retrieve tamper-evident
AI Decision Receipts via the Signatrust API. They are designed to be added to
any agent's toolset so that high-stakes decisions produce independently
verifiable evidence — without exposing prompts, model outputs, or sensitive
business data (only SHA-256 hashes are stored by default).

Example:
    from langchain_signatrust import SignatrustGenerateReceiptTool

    tool = SignatrustGenerateReceiptTool(api_key="sk_live_...")
    receipt = tool.invoke({
        "agent_name": "LoanApprovalAgent",
        "action": "Approved loan application",
        "decision": "APPROVED: applicant meets credit policy v3",
        "risk_level": "high",
        "human_review": True,
    })
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .client import SignatrustClient

RISK_LEVELS = ("low", "medium", "high", "critical")


# ─── Generate Decision Receipt ──────────────────────────────────────────────
class GenerateReceiptInput(BaseModel):
    """Input schema for generating a Signatrust AI Decision Receipt."""

    agent_name: str = Field(
        description="Display name of the AI agent that made the decision, e.g. 'LoanApprovalAgent'."
    )
    action: str = Field(
        description="Short description of the action the AI agent took, e.g. 'Approved loan application'."
    )
    decision: str = Field(
        description=(
            "The output or result returned by the AI agent (JSON or plain text). "
            "Only its SHA-256 hash is stored unless raw retention is enabled."
        )
    )
    workflow_name: Optional[str] = Field(
        default=None,
        description="Optional name of the workflow or chain in which the decision was made.",
    )
    model_provider: Optional[str] = Field(
        default=None, description="AI provider that hosts the model, e.g. 'openai', 'anthropic'."
    )
    model_name: Optional[str] = Field(
        default=None, description="AI model that generated the decision, e.g. 'gpt-4o'."
    )
    model_version: Optional[str] = Field(
        default=None, description="Version tag of the AI model, e.g. '2025-08-01'."
    )
    decision_type: Optional[str] = Field(
        default=None,
        description="A semantic label categorising the decision, e.g. 'loan_decision', 'refund_approval'.",
    )
    risk_level: Optional[str] = Field(
        default=None,
        description="Risk classification of the decision: one of 'low', 'medium', 'high', 'critical'.",
    )
    human_review: Optional[bool] = Field(
        default=None,
        description="Whether a human reviewed the decision before it was finalised.",
    )
    policies: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Policies that govern this decision, e.g. ['eu-ai-act-high-risk', 'internal-credit-v3'].",
    )
    permissions: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Permissions the agent exercised, e.g. ['credit.decide', 'payments.execute'].",
    )
    tags: Optional[Union[str, List[str]]] = Field(
        default=None, description="Tags to categorise this receipt, e.g. ['finance', 'high-value']."
    )
    include_decision_in_metadata: bool = Field(
        default=False,
        description=(
            "If True, also store the raw decision text inside the receipt metadata. "
            "Off by default (privacy-first: only the SHA-256 hash is stored)."
        ),
    )


class SignatrustGenerateReceiptTool(BaseTool):
    """Generate a cryptographically signed AI Decision Receipt with Signatrust.

    Use this tool to seal an AI-assisted decision into a tamper-evident receipt
    that regulators, auditors, or counterparties can independently verify —
    without exposing the underlying prompt, model output, or business data.
    """

    name: str = "signatrust_generate_receipt"
    description: str = (
        "Generate a cryptographically signed, tamper-evident AI Decision Receipt for an "
        "AI-assisted decision. Records which AI system was involved, the action taken, "
        "policies/permissions in effect, and whether a human reviewed it. Returns a "
        "receipt_id and a public verify_url. Use this after making a high-stakes or "
        "regulated decision to create independently verifiable evidence."
    )
    args_schema: Type[BaseModel] = GenerateReceiptInput

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30

    _client: Optional[SignatrustClient] = None

    def _get_client(self) -> SignatrustClient:
        if self._client is None:
            self._client = SignatrustClient(
                api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
            )
        return self._client

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
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        if risk_level is not None and risk_level not in RISK_LEVELS:
            raise ValueError(
                f"risk_level must be one of {RISK_LEVELS}, got {risk_level!r}"
            )
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


# ─── Verify Decision Receipt ────────────────────────────────────────────────
class ReceiptIdInput(BaseModel):
    """Input schema for verifying or fetching a receipt by its id."""

    receipt_id: str = Field(
        description="The unique Signatrust receipt ID, e.g. 'STR-1A2B3C4D5E'."
    )


class SignatrustVerifyReceiptTool(BaseTool):
    """Verify the authenticity and integrity of an existing Signatrust receipt."""

    name: str = "signatrust_verify_receipt"
    description: str = (
        "Verify the authenticity and integrity of an existing Signatrust AI Decision "
        "Receipt by its ID. Returns whether the receipt's cryptographic signature is "
        "valid and the record has not been altered."
    )
    args_schema: Type[BaseModel] = ReceiptIdInput

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30

    _client: Optional[SignatrustClient] = None

    def _get_client(self) -> SignatrustClient:
        if self._client is None:
            self._client = SignatrustClient(
                api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
            )
        return self._client

    def _run(
        self,
        receipt_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        return self._get_client().verify_receipt(receipt_id)


# ─── Get Decision Receipt ───────────────────────────────────────────────────
class SignatrustGetReceiptTool(BaseTool):
    """Retrieve the full details of a Signatrust receipt by its id."""

    name: str = "signatrust_get_receipt"
    description: str = (
        "Retrieve the full details of a Signatrust AI Decision Receipt by its ID, "
        "including its metadata, signature, hash, and verification URL."
    )
    args_schema: Type[BaseModel] = ReceiptIdInput

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30

    _client: Optional[SignatrustClient] = None

    def _get_client(self) -> SignatrustClient:
        if self._client is None:
            self._client = SignatrustClient(
                api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
            )
        return self._client

    def _run(
        self,
        receipt_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        return self._get_client().get_receipt(receipt_id)


def get_signatrust_tools(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 30,
) -> List[BaseTool]:
    """Convenience helper returning all three Signatrust tools, ready to add to an agent.

    Example:
        tools = get_signatrust_tools(api_key="sk_live_...")
        agent = create_react_agent(llm, tools)
    """
    kwargs = {"api_key": api_key, "base_url": base_url, "timeout": timeout}
    return [
        SignatrustGenerateReceiptTool(**kwargs),
        SignatrustVerifyReceiptTool(**kwargs),
        SignatrustGetReceiptTool(**kwargs),
    ]
