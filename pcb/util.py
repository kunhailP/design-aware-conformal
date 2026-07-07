"""Shared utilities."""
from __future__ import annotations
import hashlib


def det_seed(*parts) -> int:
    """A deterministic 31-bit RNG seed from arbitrary parts.

    Python's built-in ``hash()`` salts str/bytes per process (PYTHONHASHSEED), so
    ``hash(("tag", k))`` yields different seeds across runs and breaks bit-level
    reproducibility. This hashes ``repr(parts)`` with blake2b instead, so the same
    inputs always map to the same seed — on any machine, any run.
    """
    digest = hashlib.blake2b(repr(parts).encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big") % (2 ** 31)
