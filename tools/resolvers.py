from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from auth import CanvasAPIError
from tools.common import (
    candidate_ids_for_lookup,
    canvas_client,
    expand_canvas_id,
    extract_discussion_topic_id,
    id_aliases,
    is_forbidden_error,
    is_not_found_error,
    missing_argument,
    parse_canvas_course_resource,
    parse_canvas_url_path,
    recommended_tool_for_resource,
    tool_error,
)


@dataclass(slots=True)
class DiscussionTopicContext:
    topic_candidates: list[str]
    resolved_topic: dict[str, Any] | None
    assignment_linked_topic_id: str | None
    canonical_topic: dict[str, Any] | None
    view: dict[str, Any] | None
    last_error: CanvasAPIError | None
    canonical_error: CanvasAPIError | None


def _dedupe_ids(ids: list[str]) -> list[str]:
    ordered: list[str] = []
    for value in ids:
        if value and value not in ordered:
            ordered.append(value)
    return ordered


def _try_discussion_view(
    client: Any, *, course_id: str, candidates: list[str]
) -> tuple[dict[str, Any] | None, CanvasAPIError | None]:
    last_error: CanvasAPIError | None = None
    for candidate in candidates:
        try:
            return client.get_discussion_topic_view(
                course_id=course_id,
                topic_id=candidate,
            ), None
        except CanvasAPIError as exc:
            last_error = exc
    return None, last_error


def _try_discussion_topic(
    client: Any, *, course_id: str, candidates: list[str]
) -> tuple[dict[str, Any] | None, CanvasAPIError | None]:
    last_error: CanvasAPIError | None = None
    for candidate in candidates:
        try:
            return client.get_discussion_topic(
                course_id=course_id,
                topic_id=candidate,
            ), None
        except CanvasAPIError as exc:
            last_error = exc
    return None, last_error


def _find_topic_in_list(
    topics: list[dict[str, Any]],
    *,
    course_id: str,
    topic_candidates: list[str],
) -> dict[str, Any] | None:
    for topic in topics:
        topic_aliases = id_aliases(str(topic.get("id", "")), course_id=course_id)
        assignment_id = (
            str(topic["assignment_id"])
            if topic.get("assignment_id") is not None
            else ""
        )
        assignment_aliases = id_aliases(assignment_id, course_id=course_id)
        if any(
            candidate in topic_aliases or candidate in assignment_aliases
            for candidate in topic_candidates
        ):
            return topic
    return None


def resolve_discussion_topic_context(
    course_id: str,
    topic_id: str,
    *,
    client: Any | None = None,
) -> DiscussionTopicContext:
    api_client = client or canvas_client()
    topic_candidates = candidate_ids_for_lookup(topic_id, course_id=course_id)
    request_ids = list(topic_candidates)
    resolved_topic: dict[str, Any] | None = None
    assignment_linked_topic_id: str | None = None

    view, last_error = _try_discussion_view(
        api_client, course_id=course_id, candidates=request_ids
    )
    if view is not None:
        canonical_topic: dict[str, Any] | None = None
        canonical_error: CanvasAPIError | None = None
        # The view payload sometimes omits topic metadata (title, message,
        # assignment_id); only fetch the canonical topic when needed.
        if not str(view.get("title") or "").strip():
            canonical_topic, canonical_error = _try_discussion_topic(
                api_client, course_id=course_id, candidates=request_ids
            )
        return DiscussionTopicContext(
            topic_candidates=topic_candidates,
            resolved_topic=resolved_topic,
            assignment_linked_topic_id=assignment_linked_topic_id,
            canonical_topic=canonical_topic,
            view=view,
            last_error=last_error,
            canonical_error=canonical_error,
        )

    for assignment_candidate in topic_candidates:
        try:
            assignment = api_client.get_assignment(
                course_id=course_id,
                assignment_id=assignment_candidate,
                include_submission=False,
                include_discussion_topic=True,
            )
        except CanvasAPIError:
            continue
        discussion_topic_id = extract_discussion_topic_id(assignment)
        if not discussion_topic_id:
            continue
        assignment_linked_topic_id = discussion_topic_id
        linked_ids = candidate_ids_for_lookup(
            discussion_topic_id, course_id=course_id
        )
        request_ids = _dedupe_ids([*linked_ids, *request_ids])
        if isinstance(assignment.get("discussion_topic"), dict):
            resolved_topic = assignment.get("discussion_topic")
        break

    view, last_error = _try_discussion_view(
        api_client, course_id=course_id, candidates=request_ids
    )
    canonical_topic, canonical_error = _try_discussion_topic(
        api_client, course_id=course_id, candidates=request_ids
    )

    if view is None and canonical_topic is None:
        try:
            listed_topics = api_client.list_discussion_topics(
                course_id=course_id,
                include_announcements=True,
                limit=300,
            )
        except CanvasAPIError as exc:
            if last_error is None:
                last_error = exc
        else:
            resolved_topic = _find_topic_in_list(
                listed_topics,
                course_id=course_id,
                topic_candidates=topic_candidates,
            )
            if resolved_topic and resolved_topic.get("id") is not None:
                request_ids = _dedupe_ids(
                    [
                        *candidate_ids_for_lookup(
                            str(resolved_topic["id"]), course_id=course_id
                        ),
                        *request_ids,
                    ]
                )
                view, view_error = _try_discussion_view(
                    api_client, course_id=course_id, candidates=request_ids
                )
                if view_error is not None:
                    last_error = view_error
                if canonical_topic is None:
                    canonical_topic, canonical_error = _try_discussion_topic(
                        api_client, course_id=course_id, candidates=request_ids
                    )

    if canonical_topic and canonical_topic.get("id") is not None:
        request_ids = _dedupe_ids(
            [
                *candidate_ids_for_lookup(
                    str(canonical_topic.get("id")), course_id=course_id
                ),
                *request_ids,
            ]
        )
        if view is None:
            view, view_error = _try_discussion_view(
                api_client, course_id=course_id, candidates=request_ids
            )
            if view_error is not None:
                last_error = view_error

    return DiscussionTopicContext(
        topic_candidates=topic_candidates,
        resolved_topic=resolved_topic,
        assignment_linked_topic_id=assignment_linked_topic_id,
        canonical_topic=canonical_topic,
        view=view,
        last_error=last_error,
        canonical_error=canonical_error,
    )


def discussion_topic_context_error(
    *,
    topic_id: str,
    context: DiscussionTopicContext,
    not_found_message: str,
) -> dict[str, Any] | None:
    if context.view is not None:
        return None

    if context.last_error and is_forbidden_error(context.last_error):
        return tool_error(
            "forbidden",
            str(context.last_error),
            hint="Your Canvas role/token does not allow reading this discussion.",
        )
    if (
        context.last_error
        and is_not_found_error(context.last_error)
        and context.canonical_topic is None
    ):
        return tool_error("not_found", str(context.last_error), topic_id=topic_id)
    if context.canonical_topic:
        return None
    if context.canonical_error and is_forbidden_error(context.canonical_error):
        return tool_error(
            "forbidden",
            str(context.canonical_error),
            hint="Your Canvas role/token does not allow reading this discussion.",
        )
    if context.canonical_error and is_not_found_error(context.canonical_error):
        return tool_error("not_found", str(context.canonical_error), topic_id=topic_id)
    return tool_error("not_found", not_found_message, topic_id=topic_id)


def resolve_canvas_resource_details(
    *,
    course_id: str,
    resource_type: str,
    resource_id: str | None,
    resource_id_raw: str | None,
) -> dict[str, Any] | None:
    from tools.assignments import get_assignment_details
    from tools.courses import (
        get_course_overview,
        get_course_syllabus,
        list_course_pages,
        list_course_people,
    )
    from tools.discussions import get_discussion_entries, list_discussion_topics
    from tools.grades import get_course_grade_summary
    from tools.submissions import list_course_submissions

    if resource_type == "course":
        return get_course_overview({"course_id": course_id})
    if resource_type == "front_page":
        page = canvas_client().get_front_page(course_id=course_id)
        return {
            "course_id": course_id,
            "page": {
                "page_id": str(page.get("page_id", "")),
                "url": page.get("url"),
                "title": page.get("title"),
                "html_url": page.get("html_url"),
                "body": page.get("body"),
            },
        }
    if resource_type == "syllabus":
        return get_course_syllabus({"course_id": course_id, "include_body": True})
    if resource_type == "course_grades":
        return get_course_grade_summary({"course_id": course_id})
    if resource_type == "course_people":
        return list_course_people({"course_id": course_id, "limit": 100})
    if resource_type == "discussion_topics_index":
        return list_discussion_topics({"course_id": course_id, "limit": 100})
    if resource_type == "pages_index":
        return list_course_pages({"course_id": course_id, "limit": 100})
    if resource_type == "assignment" and resource_id:
        return get_assignment_details(
            {"course_id": course_id, "assignment_id": resource_id}
        )
    if resource_type == "discussion_topic" and resource_id:
        return get_discussion_entries(
            {"course_id": course_id, "topic_id": resource_id}
        )
    if resource_type == "page" and resource_id_raw:
        page = canvas_client().get_page(
            course_id=course_id,
            url_or_id=resource_id_raw,
            force_as_id=False,
        )
        return {
            "course_id": course_id,
            "page": {
                "page_id": str(page.get("page_id", "")),
                "url": page.get("url"),
                "title": page.get("title"),
                "html_url": page.get("html_url"),
            },
        }
    if resource_type == "file" and resource_id:
        for candidate in candidate_ids_for_lookup(resource_id, course_id=course_id):
            try:
                file_info = canvas_client().get_file(
                    course_id=course_id,
                    file_id=candidate,
                )
                return {
                    "course_id": course_id,
                    "file": {
                        "id": str(file_info.get("id", "")),
                        "display_name": file_info.get("display_name"),
                        "filename": file_info.get("filename"),
                        "size": file_info.get("size"),
                        "url": file_info.get("url"),
                    },
                }
            except CanvasAPIError:
                continue
        return None
    if resource_type == "assignment_submission":
        return list_course_submissions({"course_id": course_id, "limit": 200})
    return None


def resolve_canvas_url(args: dict[str, Any]) -> dict[str, Any]:
    url = str(args.get("url", "")).strip()
    if not url:
        return missing_argument("url")

    parsed, path, parts = parse_canvas_url_path(url)
    course_id_raw, resource_type, resource_id_raw = parse_canvas_course_resource(parts)
    course_id = str(course_id_raw).strip() if course_id_raw else None
    resource_id = (
        expand_canvas_id(resource_id_raw, course_id=course_id) if resource_id_raw else None
    )
    recommended_tool = recommended_tool_for_resource(resource_type)

    fetch_details = bool(args.get("fetch_details", True))
    details: dict[str, Any] | None = None
    detail_error: str | None = None
    if fetch_details and course_id and resource_type:
        try:
            details = resolve_canvas_resource_details(
                course_id=course_id,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_id_raw=resource_id_raw,
            )
        except CanvasAPIError as exc:
            detail_error = str(exc)

    return {
        "url": url,
        "domain": parsed.netloc,
        "path": path,
        "course_id_raw": course_id_raw,
        "course_id": course_id,
        "course_id_aliases": id_aliases(course_id_raw or "", course_id=course_id),
        "resource_type": resource_type,
        "resource_id_raw": resource_id_raw,
        "resource_id": resource_id,
        "resource_id_aliases": id_aliases(resource_id_raw or "", course_id=course_id),
        "recommended_tool": recommended_tool,
        "details": details,
        "detail_error": detail_error,
    }
