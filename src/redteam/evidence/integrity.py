"""Evidence integrity — SHA-256 hashing and verification.

All evidence artifacts MUST be hashed at collection time.  The hash is
stored in the evidence manifest and used for integrity verification
throughout the evidence lifecycle.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from redteam.core.errors import EvidenceIntegrityError

logger = logging.getLogger(__name__)

# Buffer size for streaming hash computation
_HASH_BUFFER_SIZE = 65536  # 64 KB


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hash of a file.

    Args:
        file_path: Path to the file to hash.

    Returns:
        Lowercase hex digest string.

    Raises:
        EvidenceIntegrityError: If the file cannot be read.
    """
    if not file_path.exists():
        raise EvidenceIntegrityError(f"File not found: {file_path}")

    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(_HASH_BUFFER_SIZE)
                if not data:
                    break
                sha256.update(data)
    except OSError as exc:
        raise EvidenceIntegrityError(f"Cannot read file {file_path}: {exc}") from exc

    digest = sha256.hexdigest()
    logger.debug("SHA-256(%s) = %s", file_path.name, digest)
    return digest


def compute_sha256_bytes(data: bytes) -> str:
    """Compute the SHA-256 hash of raw bytes.

    Returns:
        Lowercase hex digest string.
    """
    return hashlib.sha256(data).hexdigest()


def verify_sha256(file_path: Path, expected_hash: str) -> bool:
    """Verify that a file matches an expected SHA-256 hash.

    Args:
        file_path: Path to the file to verify.
        expected_hash: Expected lowercase hex digest.

    Returns:
        True if the hash matches.

    Raises:
        EvidenceIntegrityError: If the file cannot be read or hash mismatches.
    """
    actual = compute_sha256(file_path)
    if actual != expected_hash.lower():
        raise EvidenceIntegrityError(
            f"Integrity check failed for {file_path.name}: "
            f"expected {expected_hash}, got {actual}"
        )
    logger.info("Integrity verified: %s", file_path.name)
    return True
