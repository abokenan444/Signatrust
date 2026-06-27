"""autogen-signatrust — AutoGen tools for Signatrust AI Decision Receipts.

Generate, verify, and retrieve cryptographically signed (Ed25519), tamper-evident
AI Decision Receipts from within any AutoGen agent.
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
