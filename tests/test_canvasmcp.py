"""Comprehensive tests for canvasmcp.

Run with: .venv/bin/python -m pytest tests/ -v
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest
from typer.testing import CliRunner


# ---------------------------------------------------------------------------
# chrome_cookies tests
# ---------------------------------------------------------------------------


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


class TestReadChromeCookies:
    """Tests for the browser_cookie3 adapter."""

    def test_reads_matching_domain(self):
        from chrome_cookies import read_chrome_cookies

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "session123", ".umd.instructure.com"),
            cookie("_csrf_token", "csrf456", ".umd.instructure.com"),
        ]
        with mock.patch("chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert read_chrome_cookies("https://umd.instructure.com") == (
                "session123",
                "csrf456",
            )

    def test_detect_canvas_base_url_requires_unique_match(self):
        from chrome_cookies import detect_canvas_base_url

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "session123", ".umd.instructure.com"),
            cookie("_csrf_token", "csrf456", ".umd.instructure.com"),
        ]
        with mock.patch("chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert detect_canvas_base_url() == "https://umd.instructure.com"

    def test_detect_canvas_base_url_returns_none_for_multiple_domains(self):
        from chrome_cookies import detect_canvas_base_url

        def cookie(name: str, value: str, domain: str):
            return type("Cookie", (), {"name": name, "value": value, "domain": domain})()

        cookies = [
            cookie("canvas_session", "a", ".umd.instructure.com"),
            cookie("_csrf_token", "b", ".umd.instructure.com"),
            cookie("canvas_session", "c", ".school.instructure.com"),
            cookie("_csrf_token", "d", ".school.instructure.com"),
        ]
        with mock.patch("chrome_cookies.browser_cookie3.chrome", return_value=cookies):
            assert detect_canvas_base_url() is None


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
    """Tests for Chrome auth configuration."""

    def test_chrome_cookies_first(self):
        cookies = ("session", "csrf")
        with (
            mock.patch("canvas_api._resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("canvas_api._read_chrome_cookies", return_value=cookies),
        ):
            from canvas_api import ensure_canvas_auth_configured

            result = ensure_canvas_auth_configured()
            assert result == "chrome-session"

    def test_raises_when_no_chrome_cookies(self):
        with (
            mock.patch("canvas_api._resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("canvas_api._read_chrome_cookies", return_value=None),
        ):
            from canvas_api import CanvasAPIError, ensure_canvas_auth_configured

            with pytest.raises(CanvasAPIError):
                ensure_canvas_auth_configured()

    def test_uses_env_base_url_override(self):
        with mock.patch.dict(
            os.environ,
            {"CANVAS_BASE_URL": "https://umd.instructure.com"},
            clear=True,
        ):
            from canvas_api import _resolve_canvas_base_url

            assert _resolve_canvas_base_url() == "https://umd.instructure.com"

    def test_uses_detected_base_url_when_env_unset(self):
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch(
                "chrome_cookies.detect_canvas_base_url",
                return_value="https://umd.instructure.com",
            ),
        ):
            from canvas_api import _resolve_canvas_base_url

            assert _resolve_canvas_base_url() == "https://umd.instructure.com"


class TestCreateCanvasClientFromEnv:
    """Tests for create_canvas_client_from_env."""

    def test_chrome_cookies_sets_cookie_provider(self):
        cookies = ("session_val", "csrf_val")
        with (
            mock.patch("canvas_api._resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("canvas_api._read_chrome_cookies", return_value=cookies),
        ):
            from canvas_api import create_canvas_client_from_env

            client = create_canvas_client_from_env()
            assert client.cookie_provider is not None
            assert client.cookie_provider() == cookies
            assert client.base_url == "https://umd.instructure.com"

    def test_raises_without_chrome_cookies(self):
        with (
            mock.patch("canvas_api._resolve_canvas_base_url", return_value="https://umd.instructure.com"),
            mock.patch("canvas_api._read_chrome_cookies", return_value=None),
        ):
            from canvas_api import CanvasAPIError, create_canvas_client_from_env

            with pytest.raises(CanvasAPIError):
                create_canvas_client_from_env()


class TestGeneratedCli:
    """Smoke tests for the direct Typer CLI."""

    def test_tool_list_outputs_known_tool(self):
        import canvas_cli

        runner = CliRunner()
        result = runner.invoke(canvas_cli.app, ["tool", "list"])
        assert result.exit_code == 0
        assert "list_courses" in result.stdout

    def test_main_invokes_app(self):
        import canvas_cli

        with mock.patch.object(canvas_cli, "app") as app:
            canvas_cli.main()
            app.assert_called_once_with()

    def test_courses_command_dispatches_expected_args(self):
        import canvas_cli

        runner = CliRunner()
        with (
            mock.patch.object(canvas_cli, "_ensure_auth"),
            mock.patch.object(canvas_cli, "dispatch_tool_call") as dispatch,
        ):
            dispatch.return_value = {"count": 0, "courses": []}
            result = runner.invoke(canvas_cli.app, ["courses", "--all", "--limit", "10"])
        assert result.exit_code == 0
        dispatch.assert_called_once_with(
            "list_courses",
            {"favorites_only": False, "search": None, "limit": 10},
        )

    def test_today_does_not_require_auth(self):
        import canvas_cli

        runner = CliRunner()
        with (
            mock.patch.object(canvas_cli, "_ensure_auth") as ensure_auth,
            mock.patch.object(canvas_cli, "dispatch_tool_call") as dispatch,
        ):
            dispatch.return_value = {"today": "2026-03-10"}
            result = runner.invoke(canvas_cli.app, ["today"])
        assert result.exit_code == 0
        ensure_auth.assert_not_called()

    def test_auth_status_reports_env_override(self):
        import canvas_cli

        runner = CliRunner()
        with (
            mock.patch.dict(os.environ, {"CANVAS_BASE_URL": "https://umd.instructure.com"}),
            mock.patch.object(canvas_cli, "ensure_canvas_auth_configured", return_value="chrome-session"),
        ):
            result = runner.invoke(canvas_cli.app, ["auth-status"])
            assert result.exit_code == 0
            assert "chrome-session" in result.stdout
            assert "umd.instructure.com" in result.stdout


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
