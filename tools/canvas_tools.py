from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from specs.registry import dispatch_tool_call as _dispatch_tool_call
from tools import assignments, common, courses, discussions, files, misc

_normalize = common.normalize
_clamp = common.clamp
_expand_canvas_id = common.expand_canvas_id
_collapse_canvas_id = common.collapse_canvas_id
_short_canvas_id = common.short_canvas_id
_id_aliases = common.id_aliases
_candidate_ids_for_lookup = common.candidate_ids_for_lookup
_extract_discussion_topic_id = common.extract_discussion_topic_id
_is_forbidden_message = common.is_forbidden_message
_is_not_found_message = common.is_not_found_message
_first_non_none = common.first_non_none
_map_discussion_entry = common.map_discussion_entry
_count_discussion_entries = common.count_discussion_entries
_relevance_score = courses.relevance_score


def _canvas_client():
    return common.canvas_client()


@contextmanager
def _patched_canvas_client():
    modules = [common, assignments, courses, discussions, files, misc]
    originals = [module.canvas_client for module in modules]
    try:
        for module in modules:
            module.canvas_client = _canvas_client
        yield
    finally:
        for module, original in zip(modules, originals):
            module.canvas_client = original


def _call(handler, args: dict[str, Any]) -> dict[str, Any]:
    with _patched_canvas_client():
        return handler(args)


def get_today(args: dict[str, Any]) -> dict[str, Any]:
    return misc.get_today(args)


def list_courses(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.list_courses, args)


def resolve_course(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.resolve_course, args)


def list_course_assignments(args: dict[str, Any]) -> dict[str, Any]:
    return _call(assignments.list_course_assignments, args)


def get_assignment_details(args: dict[str, Any]) -> dict[str, Any]:
    return _call(assignments.get_assignment_details, args)


def get_assignment_rubric(args: dict[str, Any]) -> dict[str, Any]:
    return _call(assignments.get_assignment_rubric, args)


def list_course_files(args: dict[str, Any]) -> dict[str, Any]:
    return _call(files.list_course_files, args)


def download_course_file(args: dict[str, Any]) -> dict[str, Any]:
    return _call(files.download_course_file, args)


def list_course_folders(args: dict[str, Any]) -> dict[str, Any]:
    return _call(files.list_course_folders, args)


def list_modules(args: dict[str, Any]) -> dict[str, Any]:
    return _call(files.list_modules, args)


def canvas_get_page(args: dict[str, Any]) -> dict[str, Any]:
    return _call(misc.canvas_get_page, args)


def list_announcements(args: dict[str, Any]) -> dict[str, Any]:
    return _call(misc.list_announcements, args)


def list_calendar_events(args: dict[str, Any]) -> dict[str, Any]:
    return _call(misc.list_calendar_events, args)


def list_course_people(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.list_course_people, args)


def get_course_overview(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.get_course_overview, args)


def get_course_syllabus(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.get_course_syllabus, args)


def list_course_pages(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.list_course_pages, args)


def list_course_tabs(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.list_course_tabs, args)


def get_course_tab(args: dict[str, Any]) -> dict[str, Any]:
    return _call(courses.get_course_tab, args)


def list_discussion_topics(args: dict[str, Any]) -> dict[str, Any]:
    return _call(discussions.list_discussion_topics, args)


def get_discussion_entries(args: dict[str, Any]) -> dict[str, Any]:
    return _call(discussions.get_discussion_entries, args)


def list_assignment_groups(args: dict[str, Any]) -> dict[str, Any]:
    return _call(assignments.list_assignment_groups, args)


def list_course_submissions(args: dict[str, Any]) -> dict[str, Any]:
    return _call(assignments.list_course_submissions, args)


def get_course_grade_summary(args: dict[str, Any]) -> dict[str, Any]:
    return _call(assignments.get_course_grade_summary, args)


def resolve_canvas_url(args: dict[str, Any]) -> dict[str, Any]:
    return _call(misc.resolve_canvas_url, args)


def get_course_context_snapshot(args: dict[str, Any]) -> dict[str, Any]:
    return _call(misc.get_course_context_snapshot, args)


def dispatch_tool_call(name: str, args: dict | None = None) -> dict:
    return _dispatch_tool_call(name, args)
