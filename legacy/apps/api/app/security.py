import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Tuple


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data_str: str) -> bytes:
    padding = '=' * (-len(data_str) % 4)
    return base64.urlsafe_b64decode(data_str + padding)


def get_signing_secret() -> bytes:
    secret = os.getenv("SIGNING_SECRET")
    if not secret:
        # In dev, default to a simple secret to avoid setup friction
        secret = "dev-signing-secret-change-me"
    return secret.encode("utf-8")


def sign_payload(payload: Dict[str, Any]) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    body_b64 = _b64url_encode(body)
    mac = hmac.new(get_signing_secret(), body_b64.encode("ascii"), hashlib.sha256).digest()
    sig = _b64url_encode(mac)
    return f"{body_b64}.{sig}"


def verify_token(token: str) -> Dict[str, Any]:
    try:
        body_b64, sig_b64 = token.split(".", 1)
    except ValueError:
        raise ValueError("invalid token format")
    expected = _b64url_encode(hmac.new(get_signing_secret(), body_b64.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(sig_b64, expected):
        raise ValueError("invalid signature")
    payload_bytes = _b64url_decode(body_b64)
    payload = json.loads(payload_bytes.decode("utf-8"))
    exp = payload.get("exp")
    if isinstance(exp, (int, float)) and time.time() > float(exp):
        raise ValueError("token expired")
    return payload


