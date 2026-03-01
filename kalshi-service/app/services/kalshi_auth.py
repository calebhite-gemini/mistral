"""
Kalshi RSA-PSS authentication helpers.

Environment variables:
    KALSHI_KEY_ID          — your API key ID string
    KALSHI_PRIVATE_KEY_PEM — full PEM text of your RSA private key
"""
from __future__ import annotations

import base64
import os
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def _load_private_key():
    pem = os.environ.get("KALSHI_PRIVATE_KEY_PEM", "")
    if not pem:
        raise EnvironmentError("KALSHI_PRIVATE_KEY_PEM is not set")
    return serialization.load_pem_private_key(pem.encode(), password=None)


def build_auth_headers(method: str, path: str) -> dict[str, str]:
    """
    Return the three Kalshi auth headers for one request.

    Args:
        method: HTTP verb, e.g. "GET" or "POST"
        path:   Full path including /trade-api/v2 prefix, e.g. "/trade-api/v2/portfolio/orders"
    """
    key_id = os.environ.get("KALSHI_KEY_ID", "")
    if not key_id:
        raise EnvironmentError("KALSHI_KEY_ID is not set")

    timestamp_ms = str(int(time.time() * 1000))
    message = (timestamp_ms + method.upper() + path).encode()

    private_key = _load_private_key()
    signature_bytes = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    signature_b64 = base64.b64encode(signature_bytes).decode()

    return {
        "KALSHI-ACCESS-KEY": key_id,
        "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
        "KALSHI-ACCESS-SIGNATURE": signature_b64,
    }
