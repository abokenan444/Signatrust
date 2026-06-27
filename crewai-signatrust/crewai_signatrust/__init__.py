"""crewai-signatrust — CrewAI tools for Signatrust AI Decision Receipts.

Generate, verify, and retrieve cryptographically signed (Ed25519), tamper-evident
AI Decision Receipts from within any CrewAI agent or crew.
"""

from .client import SignatrustClient, SignatrustError
from .tools import (
    SignatrustGenerateReceiptTool,
    SignatrustGetReceiptTool,
    SignatrustVerifyReceiptTool,
    get_signatrust_tools,
)

__version__ = "0.1.0"

__all__ = [
    "SignatrustClient",
    "SignatrustError",
    "SignatrustGenerateReceiptTool",
    "SignatrustVerifyReceiptTool",
    "SignatrustGetReceiptTool",
    "get_signatrust_tools",
    "__version__",
]
