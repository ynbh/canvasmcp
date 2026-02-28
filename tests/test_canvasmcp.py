"""Comprehensive tests for canvasmcp.

Run with: .venv/bin/python -m pytest tests/ -v
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def _clear_cached_chrome_key():
    import chrome_cookies

    chrome_cookies._CACHED_CHROME_KEY = None
    yield
    chrome_cookies._CACHED_CHROME_KEY = None


# ---------------------------------------------------------------------------
# chrome_cookies tests
# ---------------------------------------------------------------------------


class TestChromeEncryptionKey:
    """Tests for _get_chrome_encryption_key."""

    def test_returns_bytes_on_success(self):
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0, stdout="my_secret_key\n")
            from chrome_cookies import _get_chrome_encryption_key

            key = _get_chrome_encryption_key()
            assert key == b"my_secret_key"

    def test_returns_none_on_failure(self):
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=1, stderr="not found")
            from chrome_cookies import _get_chrome_encryption_key

            assert _get_chrome_encryption_key() is None

    def test_returns_none_on_timeout(self):
        import subprocess

        with mock.patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 30)
        ):
            from chrome_cookies import _get_chrome_encryption_key

            assert _get_chrome_encryption_key() is None


class TestDeriveAesKey:
    """Tests for _derive_aes_key."""

    def test_derives_16_byte_key(self):
        from chrome_cookies import _derive_aes_key

        key = _derive_aes_key(b"test_password")
        assert len(key) == 16
        assert isinstance(key, bytes)

    def test_deterministic_output(self):
        from chrome_cookies import _derive_aes_key

        k1 = _derive_aes_key(b"same_password")
        k2 = _derive_aes_key(b"same_password")
        assert k1 == k2

    def test_different_passwords_different_keys(self):
        from chrome_cookies import _derive_aes_key

        k1 = _derive_aes_key(b"password1")
        k2 = _derive_aes_key(b"password2")
        assert k1 != k2


class TestDecryptCookieValue:
    """Tests for _decrypt_cookie_value."""

    def test_empty_value_returns_none(self):
        from chrome_cookies import _decrypt_cookie_value, _derive_aes_key

        aes_key = _derive_aes_key(b"test")
        assert _decrypt_cookie_value(b"", aes_key) is None

    def test_plain_utf8_value(self):
        from chrome_cookies import _decrypt_cookie_value, _derive_aes_key

        aes_key = _derive_aes_key(b"test")
        # Non-v10 prefix means plain text
        assert _decrypt_cookie_value(b"plain_cookie", aes_key) == "plain_cookie"

    def test_v10_encrypted_round_trip(self):
        """Encrypt a value with known key and verify decryption."""
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        from chrome_cookies import (
            _decrypt_cookie_value,
            _derive_aes_key,
            _IV,
            _V10_PREFIX,
        )

        password = b"test_chrome_key"
        aes_key = _derive_aes_key(password)
        plaintext = b"my_session_value"

        # PKCS7 pad to 16 bytes
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext + bytes([pad_len] * pad_len)

        cipher = Cipher(
            algorithms.AES(aes_key), modes.CBC(_IV), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        encrypted_value = _V10_PREFIX + ciphertext
        result = _decrypt_cookie_value(encrypted_value, aes_key)
        assert result == "my_session_value"

    def test_v10_with_host_hash_prefix(self):
        import hashlib

        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        from chrome_cookies import (
            _decrypt_cookie_value,
            _derive_aes_key,
            _IV,
            _V10_PREFIX,
        )

        host_key = "umd.instructure.com"
        aes_key = _derive_aes_key(b"test_chrome_key")
        plaintext = (
            hashlib.sha256(host_key.encode("utf-8")).digest() + b"csrf_token_value"
        )

        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext + bytes([pad_len] * pad_len)
        cipher = Cipher(
            algorithms.AES(aes_key), modes.CBC(_IV), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted = _V10_PREFIX + encryptor.update(padded) + encryptor.finalize()

        assert _decrypt_cookie_value(encrypted, aes_key, host_key) == "csrf_token_value"


class TestDomainFromBaseUrl:
    """Tests for _domain_from_base_url."""

    def test_extracts_hostname(self):
        from chrome_cookies import _domain_from_base_url

        assert (
            _domain_from_base_url("https://umd.instructure.com")
            == "umd.instructure.com"
        )

    def test_extracts_hostname_with_path(self):
        from chrome_cookies import _domain_from_base_url

        assert (
            _domain_from_base_url("https://canvas.school.edu/api/v1")
            == "canvas.school.edu"
        )

    def test_default_url(self):
        from chrome_cookies import _domain_from_base_url

        assert (
            _domain_from_base_url("https://canvas.instructure.com")
            == "canvas.instructure.com"
        )


class TestFindChromeProfiles:
    """Tests for _find_chrome_profiles."""

    def test_finds_default_and_numbered_profiles(self, tmp_path: Path):
        chrome_dir = tmp_path / "Google" / "Chrome"
        (chrome_dir / "Default").mkdir(parents=True)
        (chrome_dir / "Default" / "Cookies").touch()
        (chrome_dir / "Profile 1").mkdir()
        (chrome_dir / "Profile 1" / "Cookies").touch()
        (chrome_dir / "Profile 2").mkdir()
        # Profile 2 has no Cookies file

        with mock.patch("chrome_cookies._CHROME_BASE", chrome_dir):
            from chrome_cookies import _find_chrome_profiles

            profiles = _find_chrome_profiles()
            assert len(profiles) == 2
            assert profiles[0] == chrome_dir / "Default" / "Cookies"
            assert profiles[1] == chrome_dir / "Profile 1" / "Cookies"

    def test_returns_empty_when_no_chrome(self, tmp_path: Path):
        with mock.patch("chrome_cookies._CHROME_BASE", tmp_path / "nonexistent"):
            from chrome_cookies import _find_chrome_profiles

            assert _find_chrome_profiles() == []


class TestReadCookiesFromDb:
    """Tests for _read_cookies_from_db with a real SQLite file."""

    def _create_test_db(
        self, db_path: Path, cookies: list[tuple[str, str, str, bytes]]
    ):
        """Create a Chrome-like Cookies DB with test data.

        cookies: list of (host_key, name, value, encrypted_value)
        """
        conn = sqlite3.connect(str(db_path))
        conn.execute(
            "CREATE TABLE cookies ("
            "host_key TEXT, name TEXT, value TEXT, encrypted_value BLOB, "
            "path TEXT DEFAULT '/', expires_utc INTEGER DEFAULT 0, "
            "is_secure INTEGER DEFAULT 0, is_httponly INTEGER DEFAULT 0, "
            "samesite INTEGER DEFAULT 0, priority INTEGER DEFAULT 0)"
        )
        for host_key, name, value, encrypted_value in cookies:
            conn.execute(
                "INSERT INTO cookies (host_key, name, value, encrypted_value) VALUES (?, ?, ?, ?)",
                (host_key, name, value, encrypted_value),
            )
        conn.commit()
        conn.close()

    def test_reads_plain_cookies(self, tmp_path: Path):
        from chrome_cookies import _read_cookies_from_db, _derive_aes_key

        db_path = tmp_path / "Cookies"
        self._create_test_db(
            db_path,
            [
                ("umd.instructure.com", "canvas_session", "session123", b""),
                ("umd.instructure.com", "_csrf_token", "csrf456", b""),
            ],
        )
        aes_key = _derive_aes_key(b"test")
        result = _read_cookies_from_db(db_path, "umd.instructure.com", aes_key)
        assert result == {"canvas_session": "session123", "_csrf_token": "csrf456"}

    def test_reads_encrypted_cookies(self, tmp_path: Path):
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        from chrome_cookies import (
            _read_cookies_from_db,
            _derive_aes_key,
            _IV,
            _V10_PREFIX,
        )

        aes_key = _derive_aes_key(b"test_key")

        def encrypt(plaintext: str) -> bytes:
            data = plaintext.encode("utf-8")
            pad_len = 16 - (len(data) % 16)
            padded = data + bytes([pad_len] * pad_len)
            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(_IV), backend=default_backend()
            )
            enc = cipher.encryptor()
            return _V10_PREFIX + enc.update(padded) + enc.finalize()

        db_path = tmp_path / "Cookies"
        self._create_test_db(
            db_path,
            [
                ("umd.instructure.com", "canvas_session", "", encrypt("my_session")),
                ("umd.instructure.com", "_csrf_token", "", encrypt("my_csrf")),
            ],
        )
        result = _read_cookies_from_db(db_path, "umd.instructure.com", aes_key)
        assert result == {"canvas_session": "my_session", "_csrf_token": "my_csrf"}

    def test_dot_domain_match(self, tmp_path: Path):
        from chrome_cookies import _read_cookies_from_db, _derive_aes_key

        db_path = tmp_path / "Cookies"
        self._create_test_db(
            db_path,
            [
                (".umd.instructure.com", "canvas_session", "ses", b""),
                (".umd.instructure.com", "_csrf_token", "tok", b""),
            ],
        )
        aes_key = _derive_aes_key(b"test")
        result = _read_cookies_from_db(db_path, "umd.instructure.com", aes_key)
        assert result == {"canvas_session": "ses", "_csrf_token": "tok"}

    def test_no_matching_cookies(self, tmp_path: Path):
        from chrome_cookies import _read_cookies_from_db, _derive_aes_key

        db_path = tmp_path / "Cookies"
        self._create_test_db(
            db_path,
            [("other.com", "canvas_session", "val", b"")],
        )
        aes_key = _derive_aes_key(b"test")
        result = _read_cookies_from_db(db_path, "umd.instructure.com", aes_key)
        assert result == {}

    def test_prefers_latest_cookie_value(self, tmp_path: Path):
        from chrome_cookies import _read_cookies_from_db, _derive_aes_key

        db_path = tmp_path / "Cookies"
        self._create_test_db(
            db_path,
            [
                ("umd.instructure.com", "canvas_session", "old_session", b""),
                ("umd.instructure.com", "_csrf_token", "old_csrf", b""),
                ("umd.instructure.com", "canvas_session", "new_session", b""),
                ("umd.instructure.com", "_csrf_token", "new_csrf", b""),
            ],
        )
        aes_key = _derive_aes_key(b"test")
        result = _read_cookies_from_db(db_path, "umd.instructure.com", aes_key)
        assert result == {"canvas_session": "new_session", "_csrf_token": "new_csrf"}


class TestReadChromeCookies:
    """Integration-level tests for read_chrome_cookies."""

    def test_returns_none_when_no_keychain(self):
        with mock.patch("chrome_cookies._get_chrome_encryption_key", return_value=None):
            from chrome_cookies import read_chrome_cookies

            assert read_chrome_cookies("https://umd.instructure.com") is None

    def test_returns_none_when_no_profiles(self):
        with (
            mock.patch(
                "chrome_cookies._get_chrome_encryption_key", return_value=b"key"
            ),
            mock.patch("chrome_cookies._find_chrome_profiles", return_value=[]),
        ):
            from chrome_cookies import read_chrome_cookies

            assert read_chrome_cookies("https://umd.instructure.com") is None


# ---------------------------------------------------------------------------
# canvas_urls tests
# ---------------------------------------------------------------------------


class TestNormalizeCanvasApiBaseUrl:
    """Tests for normalize_canvas_api_base_url."""

    def test_adds_api_v1(self):
        from canvas_urls import normalize_canvas_api_base_url

        assert normalize_canvas_api_base_url("https://canvas.instructure.com") == (
            "https://canvas.instructure.com/api/v1"
        )

    def test_preserves_existing_api_v1(self):
        from canvas_urls import normalize_canvas_api_base_url

        assert normalize_canvas_api_base_url(
            "https://canvas.instructure.com/api/v1"
        ) == ("https://canvas.instructure.com/api/v1")

    def test_extends_api_to_v1(self):
        from canvas_urls import normalize_canvas_api_base_url

        assert normalize_canvas_api_base_url("https://canvas.instructure.com/api") == (
            "https://canvas.instructure.com/api/v1"
        )

    def test_strips_trailing_slashes(self):
        from canvas_urls import normalize_canvas_api_base_url

        result = normalize_canvas_api_base_url("https://canvas.instructure.com///")
        assert result == "https://canvas.instructure.com/api/v1"

    def test_raises_on_empty(self):
        from canvas_urls import normalize_canvas_api_base_url

        with pytest.raises(ValueError, match="empty"):
            normalize_canvas_api_base_url("   ")

    def test_raises_on_no_scheme(self):
        from canvas_urls import normalize_canvas_api_base_url

        with pytest.raises(ValueError, match="scheme"):
            normalize_canvas_api_base_url("canvas.instructure.com")


class TestCanvasRootUrl:
    """Tests for canvas_root_url."""

    def test_strips_api_v1(self):
        from canvas_urls import canvas_root_url

        assert canvas_root_url("https://canvas.instructure.com/api/v1") == (
            "https://canvas.instructure.com"
        )

    def test_strips_api(self):
        from canvas_urls import canvas_root_url

        assert canvas_root_url("https://canvas.instructure.com/api") == (
            "https://canvas.instructure.com"
        )

    def test_no_api_path(self):
        from canvas_urls import canvas_root_url

        result = canvas_root_url("https://canvas.instructure.com")
        assert result == "https://canvas.instructure.com"


# ---------------------------------------------------------------------------
# canvas_api auth tests
# ---------------------------------------------------------------------------


class TestAuthPriority:
    """Tests for auth configuration priority."""

    def test_chrome_cookies_first(self):
        """Chrome cookies should be tried before API token."""
        cookies = ("session", "csrf")
        with mock.patch("canvas_api._read_chrome_cookies", return_value=cookies):
            from canvas_api import ensure_canvas_auth_configured

            result = ensure_canvas_auth_configured()
            assert result == "chrome-session"

    def test_manual_session_second(self):
        """Manual session env vars used when Chrome fails."""
        with (
            mock.patch("canvas_api._read_chrome_cookies", return_value=None),
            mock.patch.dict(
                os.environ,
                {
                    "CANVAS_AUTH_MODE": "session",
                    "CANVAS_SESSION_COOKIE": "ses",
                    "CANVAS_CSRF_TOKEN": "csrf",
                },
            ),
        ):
            from canvas_api import ensure_canvas_auth_configured

            result = ensure_canvas_auth_configured()
            assert result == "session-cookie"

    def test_api_token_third(self):
        """API token used when both Chrome and session fail."""
        with (
            mock.patch("canvas_api._read_chrome_cookies", return_value=None),
            mock.patch.dict(
                os.environ,
                {
                    "CANVAS_API_TOKEN": "my_token",
                    "CANVAS_AUTH_MODE": "",
                },
                clear=False,
            ),
        ):
            # Clear session-related vars
            env = os.environ.copy()
            env.pop("CANVAS_SESSION_COOKIE", None)
            env.pop("CANVAS_CSRF_TOKEN", None)
            with mock.patch.dict(os.environ, env, clear=True):
                from canvas_api import ensure_canvas_auth_configured

                result = ensure_canvas_auth_configured()
                assert result == "api-token"

    def test_raises_when_nothing_configured(self):
        """Should raise CanvasAPIError when no auth is available."""
        with (
            mock.patch("canvas_api._read_chrome_cookies", return_value=None),
            mock.patch.dict(os.environ, {}, clear=True),
        ):
            from canvas_api import CanvasAPIError, ensure_canvas_auth_configured

            with pytest.raises(CanvasAPIError):
                ensure_canvas_auth_configured()


class TestCreateCanvasClientFromEnv:
    """Tests for create_canvas_client_from_env."""

    def test_chrome_cookies_sets_cookie_provider(self):
        cookies = ("session_val", "csrf_val")
        with mock.patch("canvas_api._read_chrome_cookies", return_value=cookies):
            from canvas_api import create_canvas_client_from_env

            client = create_canvas_client_from_env()
            assert client.cookie_provider is not None
            assert client.cookie_provider() == cookies

    def test_api_token_no_cookie_provider(self):
        with (
            mock.patch("canvas_api._read_chrome_cookies", return_value=None),
            mock.patch.dict(
                os.environ,
                {
                    "CANVAS_API_TOKEN": "my_token",
                    "CANVAS_AUTH_MODE": "",
                },
                clear=True,
            ),
        ):
            from canvas_api import create_canvas_client_from_env

            client = create_canvas_client_from_env()
            assert client.cookie_provider is None
            assert client.token_provider() == "my_token"


class TestReadStaticCanvasToken:
    """Tests for _read_static_canvas_token."""

    def test_reads_from_CANVAS_API_TOKEN(self):
        with mock.patch.dict(os.environ, {"CANVAS_API_TOKEN": "tok123"}, clear=True):
            from canvas_api import _read_static_canvas_token

            assert _read_static_canvas_token() == "tok123"

    def test_reads_lowercase_variant(self):
        with mock.patch.dict(os.environ, {"canvas_api_token": "tok_lower"}, clear=True):
            from canvas_api import _read_static_canvas_token

            assert _read_static_canvas_token() == "tok_lower"

    def test_returns_empty_when_unset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            from canvas_api import _read_static_canvas_token

            assert _read_static_canvas_token() == ""


class TestIsSessionMode:
    """Tests for _is_session_mode."""

    def test_true_when_set(self):
        with mock.patch.dict(os.environ, {"CANVAS_AUTH_MODE": "session"}):
            from canvas_api import _is_session_mode

            assert _is_session_mode() is True

    def test_case_insensitive(self):
        with mock.patch.dict(os.environ, {"CANVAS_AUTH_MODE": "SESSION"}):
            from canvas_api import _is_session_mode

            assert _is_session_mode() is True

    def test_false_when_unset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            from canvas_api import _is_session_mode

            assert _is_session_mode() is False


class TestReadSessionCookies:
    """Tests for _read_session_cookies."""

    def test_returns_tuple_when_both_set(self):
        with mock.patch.dict(
            os.environ,
            {
                "CANVAS_SESSION_COOKIE": "ses",
                "CANVAS_CSRF_TOKEN": "csrf",
            },
        ):
            from canvas_api import _read_session_cookies

            assert _read_session_cookies() == ("ses", "csrf")

    def test_returns_none_when_missing_csrf(self):
        with mock.patch.dict(
            os.environ,
            {
                "CANVAS_SESSION_COOKIE": "ses",
                "CANVAS_CSRF_TOKEN": "",
            },
        ):
            from canvas_api import _read_session_cookies

            assert _read_session_cookies() is None

    def test_returns_none_when_both_missing(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            from canvas_api import _read_session_cookies

            assert _read_session_cookies() is None


# ---------------------------------------------------------------------------
# canvas_tools utility function tests
# ---------------------------------------------------------------------------


class TestNormalize:
    """Tests for _normalize."""

    def test_lowercases_and_cleans(self):
        from canvas_tools import _normalize

        assert _normalize("Hello, World!") == "hello world"

    def test_empty_input(self):
        from canvas_tools import _normalize

        assert _normalize("") == ""
        assert _normalize(None) == ""

    def test_collapses_whitespace(self):
        from canvas_tools import _normalize

        assert _normalize("  lots   of   spaces  ") == "lots of spaces"


class TestClamp:
    """Tests for _clamp."""

    def test_clamps_to_range(self):
        from canvas_tools import _clamp

        assert _clamp(0, 50) == 1
        assert _clamp(500, 50) == 300
        assert _clamp(100, 50) == 100

    def test_returns_default_for_none(self):
        from canvas_tools import _clamp

        assert _clamp(None, 50) == 50

    def test_returns_default_for_invalid(self):
        from canvas_tools import _clamp

        assert _clamp("abc", 50) == 50


class TestRelevanceScore:
    """Tests for _relevance_score."""

    def test_exact_name_match(self):
        from canvas_tools import _relevance_score

        score = _relevance_score("CMSC430", {"name": "CMSC430", "course_code": ""})
        assert score == 1.0

    def test_partial_match(self):
        from canvas_tools import _relevance_score

        score = _relevance_score(
            "cmsc", {"name": "CMSC430 Spring 2026", "course_code": ""}
        )
        assert 0 < score < 1.0

    def test_no_match(self):
        from canvas_tools import _relevance_score

        score = _relevance_score("xyz", {"name": "CMSC430", "course_code": "CS430"})
        assert score == 0.0

    def test_empty_query(self):
        from canvas_tools import _relevance_score

        assert _relevance_score("", {"name": "anything"}) == 0.0


class TestCanvasIdHelpers:
    """Tests for ID expansion/collapse/alias functions."""

    def test_expand_tilde_id(self):
        from canvas_tools import _expand_canvas_id

        result = _expand_canvas_id("1133~12345")
        # Tilde-form expands to prefix + 000000 + suffix
        assert result == "113300000012345"

    def test_collapse_full_id(self):
        from canvas_tools import _collapse_canvas_id

        result = _collapse_canvas_id("113300000012345")
        assert result == "1133~12345"

    def test_short_canvas_id(self):
        from canvas_tools import _short_canvas_id

        assert _short_canvas_id("113300000012345") == "12345"
        assert _short_canvas_id("1133~12345") == "12345"
        assert _short_canvas_id("12345") == "12345"

    def test_id_aliases_returns_all_forms(self):
        from canvas_tools import _id_aliases

        aliases = _id_aliases("1133~12345")
        assert "1133~12345" in aliases
        assert "113300000012345" in aliases
        assert "12345" in aliases

    def test_id_aliases_empty_input(self):
        from canvas_tools import _id_aliases

        assert _id_aliases("") == []

    def test_candidate_ids_for_lookup(self):
        from canvas_tools import _candidate_ids_for_lookup

        candidates = _candidate_ids_for_lookup("1133~5", course_id="1133000000099")
        assert len(candidates) > 0
        # Expanded form should be first
        assert candidates[0] == "11330000005"


class TestMapDiscussionEntry:
    """Tests for _map_discussion_entry."""

    def test_maps_basic_entry(self):
        from canvas_tools import _map_discussion_entry

        entry = {
            "id": 123,
            "message": "Hello",
            "user_name": "Student",
            "created_at": "2026-01-01",
        }
        result = _map_discussion_entry(entry, include_replies=False)
        assert result["id"] == "123"
        assert result["message"] == "Hello"
        assert "replies" not in result

    def test_maps_with_replies(self):
        from canvas_tools import _map_discussion_entry

        entry = {
            "id": 1,
            "message": "Parent",
            "replies": [{"id": 2, "message": "Reply"}],
        }
        result = _map_discussion_entry(entry, include_replies=True)
        assert len(result["replies"]) == 1
        assert result["replies"][0]["id"] == "2"


class TestCountDiscussionEntries:
    """Tests for _count_discussion_entries."""

    def test_counts_flat(self):
        from canvas_tools import _count_discussion_entries

        entries = [{"id": 1}, {"id": 2}, {"id": 3}]
        assert _count_discussion_entries(entries) == 3

    def test_counts_nested(self):
        from canvas_tools import _count_discussion_entries

        entries = [
            {"id": 1, "replies": [{"id": 2}, {"id": 3, "replies": [{"id": 4}]}]},
        ]
        assert _count_discussion_entries(entries) == 4


class TestHelperFunctions:
    """Tests for various small helper functions."""

    def test_is_forbidden_message(self):
        from canvas_tools import _is_forbidden_message

        assert _is_forbidden_message("403 Forbidden") is True
        assert _is_forbidden_message("not authorized") is True
        assert _is_forbidden_message("success") is False

    def test_is_not_found_message(self):
        from canvas_tools import _is_not_found_message

        assert _is_not_found_message("Not Found") is True
        assert _is_not_found_message("could not find resource") is True
        assert _is_not_found_message("success") is False

    def test_first_non_none(self):
        from canvas_tools import _first_non_none

        assert _first_non_none(None, None, "hello") == "hello"
        assert _first_non_none("first", "second") == "first"
        assert _first_non_none(None, None) is None

    def test_extract_discussion_topic_id_direct(self):
        from canvas_tools import _extract_discussion_topic_id

        assert _extract_discussion_topic_id({"discussion_topic_id": 42}) == "42"

    def test_extract_discussion_topic_id_nested(self):
        from canvas_tools import _extract_discussion_topic_id

        item = {"discussion_topic": {"id": 99}}
        assert _extract_discussion_topic_id(item) == "99"

    def test_extract_discussion_topic_id_none(self):
        from canvas_tools import _extract_discussion_topic_id

        assert _extract_discussion_topic_id({}) is None


# ---------------------------------------------------------------------------
# canvas_tools tool handler tests (with mocked Canvas client)
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_canvas_client():
    """Mock the _canvas_client() cached singleton."""
    client = mock.MagicMock()
    with mock.patch("canvas_tools._canvas_client", return_value=client):
        yield client


class TestGetToday:
    """Tests for get_today tool handler."""

    def test_returns_iso_date(self):
        from canvas_tools import get_today

        result = get_today({})
        assert "today" in result
        # Should be ISO format YYYY-MM-DD
        assert len(result["today"]) == 10


class TestListCoursesTool:
    """Tests for list_courses tool handler."""

    def test_returns_mapped_courses(self, mock_canvas_client):
        mock_canvas_client.list_courses.return_value = [
            {
                "id": 123,
                "name": "Math 101",
                "course_code": "MATH101",
                "workflow_state": "active",
            },
        ]
        from canvas_tools import list_courses

        result = list_courses({"favorites_only": True, "limit": 10})
        assert result["count"] == 1
        assert result["courses"][0]["name"] == "Math 101"

    def test_empty_courses(self, mock_canvas_client):
        mock_canvas_client.list_courses.return_value = []
        from canvas_tools import list_courses

        result = list_courses({})
        assert result["count"] == 0


class TestResolveCourseTool:
    """Tests for resolve_course tool handler."""

    def test_empty_query_returns_no_matches(self, mock_canvas_client):
        from canvas_tools import resolve_course

        result = resolve_course({"query": ""})
        assert result["count"] == 0

    def test_scores_and_sorts(self, mock_canvas_client):
        mock_canvas_client.list_courses.return_value = [
            {
                "id": 1,
                "name": "CMSC430",
                "course_code": "CMSC430",
                "workflow_state": "active",
            },
            {
                "id": 2,
                "name": "ENGL101",
                "course_code": "ENGL101",
                "workflow_state": "active",
            },
        ]
        from canvas_tools import resolve_course

        result = resolve_course({"query": "CMSC430"})
        assert result["count"] >= 1
        assert result["matches"][0]["name"] == "CMSC430"


class TestListCourseAssignmentsTool:
    """Tests for list_course_assignments tool handler."""

    def test_requires_course_id(self, mock_canvas_client):
        from canvas_tools import list_course_assignments

        result = list_course_assignments({})
        assert "error" in result

    def test_returns_assignments(self, mock_canvas_client):
        mock_canvas_client.list_assignments.return_value = [
            {
                "id": 42,
                "name": "HW1",
                "due_at": "2026-03-01",
                "submission_types": ["online_upload"],
            },
        ]
        from canvas_tools import list_course_assignments

        result = list_course_assignments({"course_id": "123"})
        assert result["count"] == 1
        assert result["assignments"][0]["name"] == "HW1"


class TestGetAssignmentDetailsTool:
    """Tests for get_assignment_details tool handler."""

    def test_requires_both_ids(self, mock_canvas_client):
        from canvas_tools import get_assignment_details

        assert "error" in get_assignment_details({"course_id": "1"})
        assert "error" in get_assignment_details({"assignment_id": "1"})

    def test_returns_details(self, mock_canvas_client):
        mock_canvas_client.get_assignment.return_value = {
            "id": 42,
            "name": "Midterm",
            "description": "<p>Exam</p>",
            "points_possible": 100,
        }
        from canvas_tools import get_assignment_details

        result = get_assignment_details({"course_id": "1", "assignment_id": "42"})
        assert result["assignment"]["name"] == "Midterm"


class TestListCourseFilesTool:
    """Tests for list_course_files tool handler."""

    def test_requires_course_id(self, mock_canvas_client):
        from canvas_tools import list_course_files

        assert "error" in list_course_files({})

    def test_returns_files(self, mock_canvas_client):
        mock_canvas_client.list_files.return_value = [
            {
                "id": 1,
                "display_name": "notes.pdf",
                "content_type": "application/pdf",
                "size": 1024,
            },
        ]
        from canvas_tools import list_course_files

        result = list_course_files({"course_id": "123"})
        assert result["count"] == 1
        assert result["files"][0]["display_name"] == "notes.pdf"


class TestListCoursePagesTool:
    """Tests for list_course_pages tool handler."""

    def test_requires_course_id(self, mock_canvas_client):
        from canvas_tools import list_course_pages

        assert "error" in list_course_pages({})

    def test_returns_pages(self, mock_canvas_client):
        mock_canvas_client.list_pages.return_value = [
            {"page_id": 1, "url": "home", "title": "Home Page", "published": True},
        ]
        from canvas_tools import list_course_pages

        result = list_course_pages({"course_id": "123"})
        assert result["count"] == 1
        assert result["pages"][0]["title"] == "Home Page"


class TestListCourseTabsTool:
    """Tests for list_course_tabs tool handler."""

    def test_requires_course_id(self, mock_canvas_client):
        from canvas_tools import list_course_tabs

        assert "error" in list_course_tabs({})

    def test_returns_tabs(self, mock_canvas_client):
        mock_canvas_client.list_tabs.return_value = [
            {
                "id": "home",
                "label": "Home",
                "html_url": "https://umd.instructure.com/courses/123",
            },
            {
                "id": "syllabus",
                "label": "Syllabus",
                "html_url": "https://umd.instructure.com/courses/123/assignments/syllabus",
            },
        ]
        from canvas_tools import list_course_tabs

        result = list_course_tabs({"course_id": "123"})
        assert result["count"] == 2
        assert result["tabs"][0]["id"] == "home"
        assert result["tabs"][1]["label"] == "Syllabus"


class TestGetCourseTabTool:
    """Tests for get_course_tab tool handler."""

    def test_requires_both_params(self, mock_canvas_client):
        from canvas_tools import get_course_tab

        assert "error" in get_course_tab({"course_id": "1"})
        assert "error" in get_course_tab({"tab_id": "home"})

    def test_returns_tab_with_target(self, mock_canvas_client):
        mock_canvas_client.get_tab.return_value = {
            "id": "syllabus",
            "label": "Syllabus",
            "html_url": "https://umd.instructure.com/courses/123/assignments/syllabus",
        }
        mock_canvas_client.get_course.return_value = {
            "id": 123,
            "name": "Course",
            "course_code": "C",
            "term": {},
            "public_syllabus": False,
            "syllabus_body": "<p>Hello</p>",
            "html_url": "https://umd.instructure.com/courses/123",
        }
        from canvas_tools import get_course_tab

        result = get_course_tab({"course_id": "123", "tab_id": "syllabus"})
        assert result["tab"]["id"] == "syllabus"
        assert result["target"]["resource_type"] == "syllabus"


class TestListDiscussionTopicsTool:
    """Tests for list_discussion_topics tool handler."""

    def test_requires_course_id(self, mock_canvas_client):
        from canvas_tools import list_discussion_topics

        assert "error" in list_discussion_topics({})

    def test_returns_topics(self, mock_canvas_client):
        mock_canvas_client.list_discussion_topics.return_value = [
            {"id": 10, "title": "Week 1 Discussion", "assignment_id": 42},
        ]
        mock_canvas_client.list_assignments.return_value = []
        from canvas_tools import list_discussion_topics

        result = list_discussion_topics({"course_id": "123"})
        assert result["count"] == 1
        assert result["topics"][0]["title"] == "Week 1 Discussion"

    def test_merges_assignment_linked_topics_when_discussion_list_empty(
        self, mock_canvas_client
    ):
        mock_canvas_client.list_discussion_topics.return_value = []
        mock_canvas_client.list_assignments.return_value = [
            {
                "id": 77,
                "name": "Prompt Discussion",
                "submission_types": ["discussion_topic"],
                "discussion_topic_id": 99,
                "discussion_topic": {
                    "id": 99,
                    "title": "Prompt Discussion",
                    "message": "<p>Discuss</p>",
                    "html_url": "https://umd.instructure.com/courses/123/discussion_topics/99",
                },
            }
        ]
        from canvas_tools import list_discussion_topics

        result = list_discussion_topics({"course_id": "123"})
        assert result["count"] == 1
        assert result["topics"][0]["id"] == "99"
        assert result["topics"][0]["source"] == "assignment_linked"


class TestListAnnouncementsTool:
    """Tests for list_announcements tool handler."""

    def test_requires_course_ids(self, mock_canvas_client):
        from canvas_tools import list_announcements

        assert "error" in list_announcements({})

    def test_returns_announcements(self, mock_canvas_client):
        mock_canvas_client.list_announcements.return_value = [
            {"id": 5, "title": "Welcome!", "message": "<p>Hi</p>"},
        ]
        from canvas_tools import list_announcements

        result = list_announcements({"course_ids": ["123"]})
        assert result["count"] == 1


class TestListCalendarEventsTool:
    """Tests for list_calendar_events tool handler."""

    def test_returns_events(self, mock_canvas_client):
        mock_canvas_client.list_calendar_events.return_value = [
            {"id": 1, "title": "Midterm", "type": "assignment"},
        ]
        from canvas_tools import list_calendar_events

        result = list_calendar_events({})
        assert result["count"] == 1


class TestListCoursePeopleTool:
    """Tests for list_course_people tool handler."""

    def test_requires_course_id(self, mock_canvas_client):
        from canvas_tools import list_course_people

        assert "error" in list_course_people({})

    def test_returns_people(self, mock_canvas_client):
        mock_canvas_client.list_course_users.return_value = [
            {"id": 1, "name": "Jane Doe", "email": "jane@umd.edu", "enrollments": []},
        ]
        from canvas_tools import list_course_people

        result = list_course_people({"course_id": "123"})
        assert result["count"] == 1
        assert result["people"][0]["name"] == "Jane Doe"


class TestResolveCanvasUrlTool:
    """Tests for resolve_canvas_url tool handler."""

    def test_requires_url(self):
        from canvas_tools import resolve_canvas_url

        assert "error" in resolve_canvas_url({})

    def test_parses_assignment_url(self):
        from canvas_tools import resolve_canvas_url

        with mock.patch("canvas_tools._canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.get_assignment.return_value = {
                "id": 42,
                "name": "HW1",
                "html_url": "...",
                "due_at": None,
                "points_possible": 10,
            }

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123/assignments/42",
                    "fetch_details": True,
                }
            )
            assert result["resource_type"] == "assignment"
            assert result["recommended_tool"] == "get_assignment_details"

    def test_parses_discussion_url(self):
        from canvas_tools import resolve_canvas_url

        with mock.patch("canvas_tools._canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.get_discussion_topic_view.return_value = {
                "id": 10,
                "title": "Discussion",
                "html_url": "...",
            }

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123/discussion_topics/10",
                    "fetch_details": True,
                }
            )
            assert result["resource_type"] == "discussion_topic"
            assert result["recommended_tool"] == "get_discussion_entries"

    def test_parses_page_url(self):
        from canvas_tools import resolve_canvas_url

        with mock.patch("canvas_tools._canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.get_page.return_value = {
                "page_id": 1,
                "url": "home",
                "title": "Home",
                "html_url": "...",
            }

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123/pages/home",
                    "fetch_details": True,
                }
            )
            assert result["resource_type"] == "page"
            assert result["recommended_tool"] == "canvas_get_page"

    def test_course_only_url(self):
        from canvas_tools import resolve_canvas_url

        with mock.patch("canvas_tools._canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            from canvas_api import CanvasAPIError

            mock_client.get_course.side_effect = CanvasAPIError("not found")

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123",
                    "fetch_details": False,
                }
            )
            assert result["resource_type"] == "course"
            assert result["recommended_tool"] == "get_course_overview"

    def test_parses_syllabus_url(self):
        from canvas_tools import resolve_canvas_url

        with mock.patch("canvas_tools._canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.get_course.return_value = {
                "id": 123,
                "name": "Course",
                "course_code": "C",
                "term": {},
                "public_syllabus": False,
                "syllabus_body": "<p>S</p>",
                "html_url": "https://umd.instructure.com/courses/123",
            }

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123/assignments/syllabus",
                    "fetch_details": True,
                }
            )
            assert result["resource_type"] == "syllabus"
            assert result["recommended_tool"] == "get_course_syllabus"

    def test_parses_people_url(self):
        from canvas_tools import resolve_canvas_url

        with mock.patch("canvas_tools._canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.list_course_users.return_value = []

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123/users",
                    "fetch_details": True,
                }
            )
            assert result["resource_type"] == "course_people"
            assert result["recommended_tool"] == "list_course_people"

    def test_parses_unknown_course_subpath(self):
        from canvas_tools import resolve_canvas_url

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123/external_tools/9",
                "fetch_details": False,
            }
        )
        assert result["resource_type"] == "course_route"
        assert result["resource_id_raw"] == "external_tools"
        assert result["recommended_tool"] is None

    def test_keeps_course_id_unexpanded(self):
        from canvas_tools import resolve_canvas_url

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/1401744/home",
                "fetch_details": False,
            }
        )
        assert result["course_id"] == "1401744"


class TestCanvasGetPageTool:
    """Tests for canvas_get_page tool handler."""

    def test_requires_both_params(self, mock_canvas_client):
        from canvas_tools import canvas_get_page

        assert "error" in canvas_get_page({"course_id": "1"})
        assert "error" in canvas_get_page({"url_or_id": "home"})

    def test_rejects_non_page_url(self, mock_canvas_client):
        from canvas_tools import canvas_get_page

        result = canvas_get_page(
            {
                "course_id": "1",
                "url_or_id": "https://umd.instructure.com/courses/1/assignments/42",
            }
        )
        assert result.get("error") == "unsupported_url_pattern"
        assert result.get("suggested_tool") == "resolve_canvas_url"

    def test_accepts_page_url(self, mock_canvas_client):
        mock_canvas_client.get_page.return_value = {
            "page_id": 1,
            "url": "home",
            "title": "Home",
        }
        from canvas_tools import canvas_get_page

        result = canvas_get_page(
            {
                "course_id": "1",
                "url_or_id": "https://umd.instructure.com/courses/1/pages/home",
            }
        )
        assert "page" in result
        assert result["page"]["title"] == "Home"


class TestDispatchToolCall:
    """Tests for dispatch_tool_call."""

    def test_unknown_tool(self):
        from canvas_tools import dispatch_tool_call

        result = dispatch_tool_call("nonexistent_tool")
        assert "error" in result
        assert "Unknown tool" in result["error"]

    def test_dispatches_get_today(self):
        from canvas_tools import dispatch_tool_call

        result = dispatch_tool_call("get_today")
        assert "today" in result
