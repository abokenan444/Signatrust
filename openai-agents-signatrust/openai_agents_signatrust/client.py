"""Lightweight HTTP client for the Signatrust REST API.

This module is intentionally dependency-light (only ``requests``) so that it can
be reused across multiple framework integrations (LangChain, CrewAI, etc.).

The Signatrust API exposes three core endpoints:

* ``POST /receipts``               – generate a signed AI Decision Receipt
* ``GET  /receipts/{id}``          – fetch a receipt by id
* ``GET  /receipts/{id}/verify``   – verify a receipt's integrity

Authentication is performed with an API key passed in the ``X-API-Key`` header.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union

import requests

DEFAULT_BASE_URL = "https://signatrust.net/api/v1"
DEFAULT_TIMEOUT = 30


class SignatrustError(RuntimeError):
    """Raised when the Signatrust API returns an error response."""


class SignatrustClient:
    """A thin, framework-agnostic client around the Signatrust REST API.

    Args:
        api_key: Your Signatrust agent API key (starts with ``sk_live_``). If not
            provided, it is read from the ``SIGNATRUST_API_KEY`` environment
            variable.
        base_url: API base URL. Defaults to Signatrust Cloud. For self-hosted
            Enterprise deployments, pass e.g.
            ``https://signatrust.your-company.com/api/v1``. May also be set via
            the ``SIGNATRUST_BASE_URL`` environment variable.
        timeout: Per-request timeout in seconds.
        session: Optional pre-configured ``requests.Session`` (useful for tests
            or custom retry/transport behaviour).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("SIGNATRUST_API_KEY")
        if not self.api_key:
            raise ValueError(
                "A Signatrust API key is required. Pass api_key=... or set the "
                "SIGNATRUST_API_KEY environment variable. Get a key at "
                "https://signatrust.net/register"
            )
        resolved_base = base_url or os.getenv("SIGNATRUST_BASE_URL") or DEFAULT_BASE_URL
        self.base_url = resolved_base.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

    # ── internal helpers ────────────────────────────────────────────────
    def _headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.request(
                method=method,
                url=url,
                headers=self._headers(),
                json=json_body,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:  # network-level failure
            raise SignatrustError(f"Signatrust request failed: {exc}") from exc

        if resp.status_code >= 400:
            detail: Union[str, Dict[str, Any]]
            try:
                detail = resp.json()
            except ValueError:
                detail = resp.text
            raise SignatrustError(
                f"Signatrust API error {resp.status_code} for {method} {path}: {detail}"
            )

        if not resp.content:
            return {}
        try:
            return resp.json()
        except ValueError as exc:
            raise SignatrustError(
                f"Signatrust returned a non-JSON response: {resp.text!r}"
            ) from exc

    # ── public API ───────────────────────────────────────────────────────
    def generate_receipt(
        self,
        *,
        agent_name: str,
        action: str,
        decision: str,
        workflow_name: Optional[str] = None,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        input_prompt: Optional[str] = None,
        decision_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        human_review: Optional[bool] = None,
        policies: Optional[Union[str, List[str]]] = None,
        permissions: Optional[Union[str, List[str]]] = None,
        tags: Optional[Union[str, List[str]]] = None,
        include_decision_in_metadata: bool = False,
    ) -> Dict[str, Any]:
        """Generate a cryptographically signed AI Decision Receipt.

        Only the SHA-256 hash of ``decision`` and ``input_prompt`` is stored by
        default; pass ``include_decision_in_metadata=True`` to also retain the
        raw decision text.

        Returns the parsed JSON receipt (``receipt_id``, ``signature``,
        ``hash``, ``verify_url``, ...).
        """
        body: Dict[str, Any] = {
            "agent_name": agent_name,
            "action": action,
            "decision": decision,
        }
        if workflow_name is not None:
            body["workflow_name"] = workflow_name

        if model_provider or model_name or model_version:
            body["model"] = {
                "provider": model_provider,
                "name": model_name,
                "version": model_version,
            }
        if input_prompt is not None:
            body["input_prompt"] = input_prompt
        if decision_type is not None:
            body["decision_type"] = decision_type
        if risk_level is not None:
            body["risk_level"] = risk_level
        if human_review is not None:
            body["human_review"] = human_review
        if policies is not None:
            body["policies"] = _csv(policies)
        if permissions is not None:
            body["permissions"] = _csv(permissions)
        if tags is not None:
            body["tags"] = _csv(tags)
        if include_decision_in_metadata:
            body["include_decision_in_metadata"] = True

        return self._request("POST", "/receipts", json_body=body)

    def get_receipt(self, receipt_id: str) -> Dict[str, Any]:
        """Fetch the full details of a receipt by its id."""
        return self._request("GET", f"/receipts/{_quote(receipt_id)}")

    def verify_receipt(self, receipt_id: str) -> Dict[str, Any]:
        """Verify the authenticity and integrity of an existing receipt."""
        return self._request("GET", f"/receipts/{_quote(receipt_id)}/verify")


def _csv(value: Union[str, List[str]]) -> str:
    """Normalise a list or comma-separated string into a comma-separated string."""
    if isinstance(value, (list, tuple)):
        return ",".join(str(v).strip() for v in value if str(v).strip())
    return str(value)


def _quote(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe="")
