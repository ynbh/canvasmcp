from __future__ import annotations


class TestNormalize:
    """Tests for _normalize."""

    def test_lowercases_and_cleans(self):
        from tools.common import normalize as _normalize

        assert _normalize("Hello, World!") == "hello world"

    def test_empty_input(self):
        from tools.common import normalize as _normalize

        assert _normalize("") == ""
        assert _normalize(None) == ""

    def test_collapses_whitespace(self):
        from tools.common import normalize as _normalize

        assert _normalize("  lots   of   spaces  ") == "lots of spaces"


class TestClamp:
    """Tests for _clamp."""

    def test_clamps_to_range(self):
        from tools.common import clamp as _clamp

        assert _clamp(0, 50) == 1
        assert _clamp(500, 50) == 300
        assert _clamp(100, 50) == 100

    def test_returns_default_for_none(self):
        from tools.common import clamp as _clamp

        assert _clamp(None, 50) == 50

    def test_returns_default_for_invalid(self):
        from tools.common import clamp as _clamp

        assert _clamp("abc", 50) == 50


class TestRelevanceScore:
    """Tests for _relevance_score."""

    def test_exact_name_match(self):
        from tools.courses import relevance_score as _relevance_score

        score = _relevance_score("CMSC430", {"name": "CMSC430", "course_code": ""})
        assert score == 1.0

    def test_partial_match(self):
        from tools.courses import relevance_score as _relevance_score

        score = _relevance_score(
            "cmsc", {"name": "CMSC430 Spring 2026", "course_code": ""}
        )
        assert 0 < score < 1.0

    def test_no_match(self):
        from tools.courses import relevance_score as _relevance_score

        score = _relevance_score("xyz", {"name": "CMSC430", "course_code": "CS430"})
        assert score == 0.0

    def test_empty_query(self):
        from tools.courses import relevance_score as _relevance_score

        assert _relevance_score("", {"name": "anything"}) == 0.0


class TestCanvasIdHelpers:
    """Tests for ID expansion/collapse/alias functions."""

    def test_expand_tilde_id(self):
        from tools.common import expand_canvas_id as _expand_canvas_id

        result = _expand_canvas_id("1133~12345")
        assert result == "113300000012345"

    def test_collapse_full_id(self):
        from tools.common import collapse_canvas_id as _collapse_canvas_id

        result = _collapse_canvas_id("113300000012345")
        assert result == "1133~12345"

    def test_short_canvas_id(self):
        from tools.common import short_canvas_id as _short_canvas_id

        assert _short_canvas_id("113300000012345") == "12345"
        assert _short_canvas_id("1133~12345") == "12345"
        assert _short_canvas_id("12345") == "12345"

    def test_id_aliases_returns_all_forms(self):
        from tools.common import id_aliases as _id_aliases

        aliases = _id_aliases("1133~12345")
        assert "1133~12345" in aliases
        assert "113300000012345" in aliases
        assert "12345" in aliases

    def test_id_aliases_empty_input(self):
        from tools.common import id_aliases as _id_aliases

        assert _id_aliases("") == []

    def test_candidate_ids_for_lookup(self):
        from tools.common import candidate_ids_for_lookup as _candidate_ids_for_lookup

        candidates = _candidate_ids_for_lookup("1133~5", course_id="1133000000099")
        assert len(candidates) > 0
        assert candidates[0] == "11330000005"


class TestMapDiscussionEntry:
    """Tests for _map_discussion_entry."""

    def test_maps_basic_entry(self):
        from tools.common import map_discussion_entry as _map_discussion_entry

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
        from tools.common import map_discussion_entry as _map_discussion_entry

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
        from tools.common import count_discussion_entries as _count_discussion_entries

        entries = [{"id": 1}, {"id": 2}, {"id": 3}]
        assert _count_discussion_entries(entries) == 3

    def test_counts_nested(self):
        from tools.common import count_discussion_entries as _count_discussion_entries

        entries = [
            {"id": 1, "replies": [{"id": 2}, {"id": 3, "replies": [{"id": 4}]}]},
        ]
        assert _count_discussion_entries(entries) == 4


class TestHelperFunctions:
    """Tests for various small helper functions."""

    def test_is_forbidden_message(self):
        from tools.common import is_forbidden_message as _is_forbidden_message

        assert _is_forbidden_message("403 Forbidden") is True
        assert _is_forbidden_message("not authorized") is True
        assert _is_forbidden_message("success") is False

    def test_is_not_found_message(self):
        from tools.common import is_not_found_message as _is_not_found_message

        assert _is_not_found_message("Not Found") is True
        assert _is_not_found_message("could not find resource") is True
        assert _is_not_found_message("success") is False

    def test_first_non_none(self):
        from tools.common import first_non_none as _first_non_none

        assert _first_non_none(None, None, "hello") == "hello"
        assert _first_non_none("first", "second") == "first"
        assert _first_non_none(None, None) is None

    def test_extract_discussion_topic_id_direct(self):
        from tools.common import (
            extract_discussion_topic_id as _extract_discussion_topic_id,
        )

        assert _extract_discussion_topic_id({"discussion_topic_id": 42}) == "42"

    def test_extract_discussion_topic_id_nested(self):
        from tools.common import (
            extract_discussion_topic_id as _extract_discussion_topic_id,
        )

        item = {"discussion_topic": {"id": 99}}
        assert _extract_discussion_topic_id(item) == "99"

    def test_extract_discussion_topic_id_none(self):
        from tools.common import (
            extract_discussion_topic_id as _extract_discussion_topic_id,
        )

        assert _extract_discussion_topic_id({}) is None
