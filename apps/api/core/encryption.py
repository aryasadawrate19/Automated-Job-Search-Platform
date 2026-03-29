"""AES-256-GCM encryption utilities for storing API keys at rest."""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from apps.api.core.config import settings


def _get_key() -> bytes:
    """Get the 32-byte AES key from environment."""
    hex_key = settings.AES_ENCRYPTION_KEY
    if not hex_key or len(hex_key) < 32:
        raise ValueError(
            "AES_ENCRYPTION_KEY must be set to a 64-char hex string (32 bytes). "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    return bytes.fromhex(hex_key[:64])


def encrypt_key(plaintext: str) -> bytes:
    """Encrypt an API key string → bytes (nonce + ciphertext)."""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ciphertext  # prepend nonce for decryption


def decrypt_key(data: bytes) -> str:
    """Decrypt bytes (nonce + ciphertext) → API key string."""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
