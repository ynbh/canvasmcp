"""Read and decrypt Canvas session cookies from Chrome's SQLite cookie DB on macOS."""

from __future__ import annotations

import hashlib
import logging
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Chrome cookie encryption constants (macOS)
_SALT = b"saltysalt"
_IV = b" " * 16  # 16 space bytes
_PBKDF2_ITERATIONS = 1003
_KEY_LENGTH = 16

# Version prefix Chrome prepends to encrypted values
_V10_PREFIX = b"v10"

# Chrome DB version >= 24 prepends a 32-byte SHA256 hash to plaintext
_SHA256_HASH_LEN = 32

# Cookie names we need
_COOKIE_NAMES = ("canvas_session", "_csrf_token")

# Chrome profile directories to search
_CHROME_BASE = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
_CACHED_CHROME_KEY: bytes | None = None


def _get_chrome_encryption_key() -> bytes | None:
    """Retrieve the Chrome Safe Storage key from the macOS Keychain.

    Returns the raw password bytes, or None if not found.
    This may trigger a macOS Keychain permission prompt.
    """
    global _CACHED_CHROME_KEY
    if _CACHED_CHROME_KEY is not None:
        return _CACHED_CHROME_KEY

    try:
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                "Chrome Safe Storage",
                "-w",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.debug("Could not read Chrome Safe Storage key: %s", result.stderr.strip())
            return None
        chrome_key = result.stdout.strip().encode("utf-8")
        if not chrome_key:
            return None
        _CACHED_CHROME_KEY = chrome_key
        return chrome_key
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        logger.debug("Failed to access Keychain: %s", exc)
        return None


def _derive_aes_key(chrome_key: bytes) -> bytes:
    """Derive AES-128 key from Chrome's Keychain password using PBKDF2."""
    return hashlib.pbkdf2_hmac(
        "sha1",
        chrome_key,
        _SALT,
        _PBKDF2_ITERATIONS,
        dklen=_KEY_LENGTH,
    )


def _decrypt_cookie_value(
    encrypted_value: bytes,
    aes_key: bytes,
    host_key: str | None = None,
) -> str | None:
    """Decrypt a Chrome cookie value (v10 AES-CBC on macOS).

    Chrome DB version >= 24 prepends a 32-byte SHA256 hash of the host_key
    to the plaintext before encryption. We strip it after decryption.

    Returns the decrypted string, or None if decryption fails.
    """
    if not encrypted_value:
        return None

    # v10 prefix indicates AES-CBC encryption on macOS
    if not encrypted_value.startswith(_V10_PREFIX):
        # Unencrypted or unknown format — try as plain text
        try:
            return encrypted_value.decode("utf-8")
        except UnicodeDecodeError:
            return None

    ciphertext = encrypted_value[len(_V10_PREFIX) :]
    if len(ciphertext) == 0:
        return None

    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(_IV),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        if decrypted:
            pad_len = decrypted[-1]
            if 1 <= pad_len <= 16 and all(b == pad_len for b in decrypted[-pad_len:]):
                decrypted = decrypted[:-pad_len]

        # Chrome DB version >= 24 prepends SHA256(host_key) before the value.
        if host_key and len(decrypted) > _SHA256_HASH_LEN:
            host_hash = hashlib.sha256(host_key.encode("utf-8")).digest()
            if decrypted.startswith(host_hash):
                decrypted = decrypted[_SHA256_HASH_LEN:]

        try:
            return decrypted.decode("utf-8")
        except UnicodeDecodeError:
            return None
    except Exception as exc:
        logger.debug("Cookie decryption failed: %s", exc)
        return None


def _find_chrome_profiles() -> list[Path]:
    """Find all Chrome profile directories that contain a Cookies file."""
    if not _CHROME_BASE.is_dir():
        return []

    profiles: list[Path] = []
    # Check Default profile
    default_cookies = _CHROME_BASE / "Default" / "Cookies"
    if default_cookies.is_file():
        profiles.append(default_cookies)

    # Check numbered profiles
    for entry in sorted(_CHROME_BASE.iterdir()):
        if entry.name.startswith("Profile ") and entry.is_dir():
            cookies_file = entry / "Cookies"
            if cookies_file.is_file():
                profiles.append(cookies_file)

    return profiles


def _read_cookies_from_db(
    db_path: Path, domain: str, aes_key: bytes
) -> dict[str, str]:
    """Read and decrypt specific cookies from a Chrome Cookies SQLite file.

    Copies the DB to a temp file first to avoid WAL lock issues with Chrome.
    Returns a dict of {cookie_name: decrypted_value}.
    """
    # Copy DB and sidecar files so reads are consistent while Chrome is running.
    tmp_dir = tempfile.mkdtemp(prefix="chrome_cookies_")
    tmp_dir_path = Path(tmp_dir)
    tmp_db = tmp_dir_path / db_path.name
    try:
        for suffix in ("", "-wal", "-shm"):
            source = Path(f"{db_path}{suffix}")
            if source.is_file():
                shutil.copy2(source, tmp_dir_path / source.name)

        conn = sqlite3.connect(str(tmp_db))
        conn.row_factory = sqlite3.Row
        try:
            # Chrome stores cookies with host_key as ".domain" or "domain"
            host_keys = [domain, f".{domain}"]
            placeholders = ",".join("?" for _ in host_keys)
            cookie_placeholders = ",".join("?" for _ in _COOKIE_NAMES)

            query = (
                f"SELECT host_key, name, value, encrypted_value "
                f"FROM cookies "
                f"WHERE host_key IN ({placeholders}) "
                f"AND name IN ({cookie_placeholders}) "
                f"ORDER BY (host_key = ?) DESC, rowid DESC"
            )
            params = [*host_keys, *_COOKIE_NAMES, domain]
            cursor = conn.execute(query, params)

            cookies: dict[str, str] = {}
            for row in cursor:
                name = row["name"]
                if name in cookies:
                    continue
                # Try plain value first
                plain_value = row["value"]
                if plain_value:
                    cookies[name] = plain_value
                else:
                    encrypted = row["encrypted_value"]
                    if encrypted:
                        decrypted = _decrypt_cookie_value(encrypted, aes_key, row["host_key"])
                        if decrypted:
                            cookies[name] = decrypted
                if len(cookies) == len(_COOKIE_NAMES):
                    break

            return cookies
        finally:
            conn.close()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _domain_from_base_url(base_url: str) -> str:
    """Extract the hostname from a Canvas base URL."""
    parsed = urlparse(base_url)
    return parsed.hostname or base_url


def read_chrome_cookies(
    base_url: str = "https://canvas.instructure.com",
) -> tuple[str, str] | None:
    """Auto-read canvas_session and _csrf_token cookies from Chrome.

    Scans all Chrome profiles for cookies matching the Canvas domain.

    Args:
        base_url: The Canvas instance URL (used to derive the cookie domain).

    Returns:
        (canvas_session, csrf_token) tuple, or None if not found.
    """
    domain = _domain_from_base_url(base_url)
    logger.debug("Looking for Chrome cookies for domain: %s", domain)

    # Get Chrome encryption key from Keychain
    chrome_key = _get_chrome_encryption_key()
    if chrome_key is None:
        logger.debug("No Chrome encryption key available")
        return None

    aes_key = _derive_aes_key(chrome_key)

    # Search all Chrome profiles
    profiles = _find_chrome_profiles()
    if not profiles:
        logger.debug("No Chrome cookie databases found")
        return None

    for db_path in profiles:
        logger.debug("Checking Chrome profile: %s", db_path.parent.name)
        try:
            cookies = _read_cookies_from_db(db_path, domain, aes_key)
        except Exception as exc:
            logger.debug("Failed to read cookies from %s: %s", db_path, exc)
            continue

        session = cookies.get("canvas_session")
        csrf = cookies.get("_csrf_token")

        if session and csrf:
            logger.info(
                "Found Canvas cookies in Chrome profile '%s' for %s",
                db_path.parent.name,
                domain,
            )
            return session, csrf

    logger.debug("No Canvas cookies found in any Chrome profile for %s", domain)
    return None
