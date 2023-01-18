from __future__ import annotations

import hashlib


def hash_id(string: str, length=6) -> str:
    """Hash a string to a short string"""
    return hashlib.sha256(string.encode()).hexdigest()[:length]
