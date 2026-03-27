from __future__ import annotations

from typing import Any

from canvas_api import CanvasAPIError
from tools.common import (
    assignment_to_discussion_topic,
    candidate_ids_for_lookup,
    canvas_client,
    clamp,
    count_discussion_entries,
    extract_discussion_topic_id,
    first_non_none,
    id_aliases,
    is_announcement_topic,
    is_forbidden_message,
    is_not_found_message,
    map_discussion_entry,
)


def list_discussion_topics(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    search_in = str(args.get("search_in", "title")).strip().lower()
    if search_in not in {"title", "title_or_message"}:
        return {"error": "search_in must be 'title' or 'title_or_message'"}

    limit = clamp(args.get("limit"), 100)
    include_announcements = bool(args.get("include_announcements", False))
    only_graded = bool(args.get("only_graded", False))
    exact_title = bool(args.get("exact_title", False))
    search_value = str(args.get("search") or "").strip()
    scan_limit = 300

    api_topics = canvas_client().list_discussion_topics(
        course_id=course_id,
        search=None,
        only_graded=False,
        exact_title=False,
        include_announcements=True,
        search_in="title",
        limit=scan_limit,
    )
    assignments = canvas_client().list_assignments(
        course_id=course_id,
        search=None,
        include_submission=False,
        include_discussion_topic=True,
        limit=scan_limit,
    )
    assignment_topics = []
    for assignment in assignments:
        topic = assignment_to_discussion_topic(assignment)
        if topic is not None:
            assignment_topics.append(topic)

    topic_by_id: dict[str, dict[str, Any]] = {}
    for topic in api_topics + assignment_topics:
        topic_id = str(topic.get("id", "")).strip()
        if topic_id and topic_id not in topic_by_id:
            topic_by_id[topic_id] = topic
    topics = list(topic_by_id.values())

    if not include_announcements:
        topics = [topic for topic in topics if not is_announcement_topic(topic)]
    if only_graded:
        topics = [topic for topic in topics if topic.get("assignment_id")]

    if search_value:
        query = search_value.casefold()
        query_aliases = set(id_aliases(search_value, course_id=course_id))

        def matches(topic: dict[str, Any]) -> bool:
            topic_aliases = set(id_aliases(str(topic.get("id", "")), course_id=course_id))
            assignment_value = topic.get("assignment_id")
            assignment_aliases = set(
                id_aliases(str(assignment_value) if assignment_value is not None else "", course_id=course_id)
            )
            if query_aliases and query_aliases & (topic_aliases | assignment_aliases):
                return True

            title = str(topic.get("title") or "")
            message = str(topic.get("message") or "")
            if exact_title:
                return title.casefold().strip() == query
            if search_in == "title_or_message":
                return query in title.casefold() or query in message.casefold()
            return query in title.casefold()

        topics = [topic for topic in topics if matches(topic)]

    items = [
        {
            "id": str(topic.get("id", "")),
            "id_aliases": id_aliases(str(topic.get("id", "")), course_id=course_id),
            "title": topic.get("title", "Untitled discussion"),
            "message": topic.get("message"),
            "posted_at": topic.get("posted_at"),
            "last_reply_at": topic.get("last_reply_at"),
            "delayed_post_at": topic.get("delayed_post_at"),
            "lock_at": topic.get("lock_at"),
            "discussion_type": topic.get("discussion_type"),
            "is_announcement": is_announcement_topic(topic),
            "published": topic.get("published"),
            "locked": topic.get("locked"),
            "pinned": topic.get("pinned"),
            "assignment_id": str(topic["assignment_id"])
            if topic.get("assignment_id") is not None
            else None,
            "assignment_id_aliases": id_aliases(
                str(topic["assignment_id"]), course_id=course_id
            )
            if topic.get("assignment_id") is not None
            else [],
            "points_possible": topic.get("points_possible"),
            "html_url": topic.get("html_url"),
            "source": topic.get("source", "discussion_topics_api"),
        }
        for topic in topics[:limit]
    ]
    return {
        "course_id": course_id,
        "count": len(items),
        "filters": {
            "search": search_value or None,
            "search_in": search_in,
            "exact_title": exact_title,
            "only_graded": only_graded,
            "include_announcements": include_announcements,
        },
        "topics": items,
    }


def get_discussion_entries(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    topic_id = str(args.get("topic_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not topic_id:
        return {"error": "topic_id is required"}

    include_replies = bool(args.get("include_replies", True))
    include_participants = bool(args.get("include_participants", True))
    limit = clamp(args.get("limit"), 200)

    topic_candidates = candidate_ids_for_lookup(topic_id, course_id=course_id)
    resolved_topic: dict[str, Any] | None = None
    try:
        all_topics = canvas_client().list_discussion_topics(
            course_id=course_id,
            include_announcements=True,
            limit=300,
        )
    except CanvasAPIError as exc:
        message = str(exc)
        if is_forbidden_message(message):
            return {
                "error": "forbidden",
                "message": message,
                "hint": "Your Canvas role/token does not allow reading this discussion.",
            }
        return {"error": message}

    for topic in all_topics:
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
            resolved_topic = topic
            break

    request_ids: list[str] = []
    if resolved_topic and resolved_topic.get("id") is not None:
        request_ids.extend(
            candidate_ids_for_lookup(str(resolved_topic["id"]), course_id=course_id)
        )
    request_ids.extend(topic_candidates)

    deduped_request_ids: list[str] = []
    for candidate in request_ids:
        if candidate and candidate not in deduped_request_ids:
            deduped_request_ids.append(candidate)

    assignment_linked_topic_id: str | None = None
    for assignment_candidate in topic_candidates:
        try:
            assignment = canvas_client().get_assignment(
                course_id=course_id,
                assignment_id=assignment_candidate,
                include_submission=False,
                include_discussion_topic=True,
            )
        except CanvasAPIError:
            continue
        discussion_topic_id = extract_discussion_topic_id(assignment)
        if discussion_topic_id:
            assignment_linked_topic_id = discussion_topic_id
            for candidate in candidate_ids_for_lookup(
                discussion_topic_id, course_id=course_id
            ):
                if candidate not in deduped_request_ids:
                    deduped_request_ids.insert(0, candidate)
            if isinstance(assignment.get("discussion_topic"), dict):
                resolved_topic = assignment.get("discussion_topic")
            break

    canonical_topic: dict[str, Any] | None = None
    canonical_error: str | None = None
    for candidate in deduped_request_ids:
        try:
            canonical_topic = canvas_client().get_discussion_topic(
                course_id=course_id,
                topic_id=candidate,
            )
            break
        except CanvasAPIError as exc:
            canonical_error = str(exc)

    if canonical_topic and canonical_topic.get("id") is not None:
        for candidate in candidate_ids_for_lookup(
            str(canonical_topic.get("id")), course_id=course_id
        ):
            if candidate not in deduped_request_ids:
                deduped_request_ids.insert(0, candidate)

    view: dict[str, Any] | None = None
    last_error: str | None = None
    for candidate in deduped_request_ids:
        try:
            view = canvas_client().get_discussion_topic_view(
                course_id=course_id,
                topic_id=candidate,
            )
            break
        except CanvasAPIError as exc:
            last_error = str(exc)

    if view is None:
        if last_error and is_forbidden_message(last_error):
            return {
                "error": "forbidden",
                "message": last_error,
                "hint": "Your Canvas role/token does not allow reading this discussion.",
            }
        if last_error and is_not_found_message(last_error) and not canonical_topic:
            return {"error": "not_found", "message": last_error, "topic_id": topic_id}
        if canonical_topic:
            view = {"view": [], "participants": []}
        else:
            if canonical_error and is_forbidden_message(canonical_error):
                return {
                    "error": "forbidden",
                    "message": canonical_error,
                    "hint": "Your Canvas role/token does not allow reading this discussion.",
                }
            if canonical_error and is_not_found_message(canonical_error):
                return {"error": "not_found", "message": canonical_error, "topic_id": topic_id}
            return {
                "error": "not_found",
                "message": (
                    "Could not resolve a discussion topic from the provided id. "
                    "Try list_discussion_topics first and pass its topic id."
                ),
                "topic_id": topic_id,
            }

    topic_view_id = str(view.get("id", "")).strip()
    if not topic_view_id and isinstance(canonical_topic, dict):
        topic_view_id = str(canonical_topic.get("id") or "").strip()
    if not topic_view_id and isinstance(resolved_topic, dict):
        topic_view_id = str(resolved_topic.get("id") or "").strip()
    if not topic_view_id:
        return {
            "error": "not_found",
            "message": (
                "Canvas returned an empty discussion payload. "
                "This usually means the id does not map to a discussion topic."
            ),
            "topic_id": topic_id,
        }

    raw_entries = [
        entry for entry in (view.get("view") or []) if isinstance(entry, dict)
    ][:limit]
    entries = [map_discussion_entry(entry, include_replies) for entry in raw_entries]

    participants = []
    if include_participants:
        participants = [
            {
                "id": str(user.get("id", "")),
                "anonymous_id": user.get("anonymous_id"),
                "display_name": user.get("display_name"),
                "avatar_image_url": user.get("avatar_image_url"),
                "html_url": user.get("html_url"),
                "pronouns": user.get("pronouns"),
            }
            for user in (view.get("participants") or [])
            if isinstance(user, dict)
        ]

    title = str(view.get("title") or "").strip()
    if not title and isinstance(canonical_topic, dict):
        title = str(canonical_topic.get("title") or "").strip()
    if not title and isinstance(resolved_topic, dict):
        title = str(resolved_topic.get("title") or "").strip()

    if (
        not title
        and not str(view.get("message") or "").strip()
        and not str((canonical_topic or {}).get("message") or "").strip()
        and not entries
        and resolved_topic is None
        and canonical_topic is None
    ):
        return {
            "error": "not_found",
            "message": (
                "Canvas did not return a valid discussion payload for this id. "
                "Pass a discussion topic id from list_discussion_topics."
            ),
            "topic_id": topic_id,
        }

    topic_message = first_non_none(
        view.get("message"),
        canonical_topic.get("message") if isinstance(canonical_topic, dict) else None,
        resolved_topic.get("message") if isinstance(resolved_topic, dict) else None,
    )
    topic_assignment_id = first_non_none(
        str(view["assignment_id"]) if view.get("assignment_id") is not None else None,
        str(canonical_topic["assignment_id"])
        if isinstance(canonical_topic, dict)
        and canonical_topic.get("assignment_id") is not None
        else None,
        str(resolved_topic["assignment_id"])
        if isinstance(resolved_topic, dict)
        and resolved_topic.get("assignment_id") is not None
        else None,
    )
    topic_discussion_type = first_non_none(
        view.get("discussion_type"),
        canonical_topic.get("discussion_type") if isinstance(canonical_topic, dict) else None,
        resolved_topic.get("discussion_type") if isinstance(resolved_topic, dict) else None,
    )
    topic_html_url = first_non_none(
        view.get("html_url"),
        canonical_topic.get("html_url") if isinstance(canonical_topic, dict) else None,
        resolved_topic.get("html_url") if isinstance(resolved_topic, dict) else None,
    )

    return {
        "course_id": course_id,
        "requested_topic_id": topic_id,
        "requested_topic_id_aliases": topic_candidates,
        "assignment_linked_topic_id": assignment_linked_topic_id,
        "resolved_topic_id": topic_view_id,
        "resolved_topic_id_aliases": id_aliases(topic_view_id, course_id=course_id),
        "topic": {
            "id": topic_view_id,
            "title": title or "Untitled discussion",
            "message": topic_message,
            "assignment_id": topic_assignment_id,
            "discussion_type": topic_discussion_type,
            "published": view.get("published"),
            "locked": view.get("locked"),
            "html_url": topic_html_url,
        },
        "participants_count": len(participants),
        "participants": participants,
        "top_level_entries_count": len(entries),
        "total_entries_count": count_discussion_entries(entries),
        "entries": entries,
    }
