"""openai-agents-signatrust — OpenAI Agents SDK tools for Signatrust Decision Receipts.

Generate, verify, and retrieve cryptographically signed (Ed25519), tamper-evident
AI Decision Receipts from within any OpenAI Agents SDK agent.
"""

from .client import SignatrustClient, SignatrustError
from .tools import (
    configure,
    get_signatrust_tools,
    signatrust_generate_receipt,
    signatrust_get_receipt,
    signatrust_verify_receipt,
)

__version__ = "0.1.0"

__all__ = [
    "SignatrustClient",
    "SignatrustError",
    "configure",
    "get_signatrust_tools",
    "signatrust_generate_receipt",
    "signatrust_verify_receipt",
    "signatrust_get_receipt",
    "__version__",
]
