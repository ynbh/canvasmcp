from __future__ import annotations

from typing import Any

from tools.common import (
    assignment_to_discussion_topic,
    canvas_client,
    clamp,
    count_discussion_entries,
    first_non_none,
    id_aliases,
    invalid_argument,
    is_announcement_topic,
    looks_like_canvas_id,
    map_discussion_entry,
    missing_argument,
    tool_error,
    truncate_html,
)
from tools.resolvers import (
    discussion_topic_context_error,
    resolve_discussion_topic_context,
)


def _map_discussion_topic_item(
    topic: dict[str, Any], *, course_id: str
) -> dict[str, Any]:
    return {
        "id": str(topic.get("id", "")),
        "id_aliases": id_aliases(str(topic.get("id", "")), course_id=course_id),
        "title": topic.get("title", "Untitled discussion"),
        "message": truncate_html(topic.get("message")),
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


def list_discussion_topics(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return missing_argument("course_id")

    search_in = str(args.get("search_in", "title")).strip().lower()
    if search_in not in {"title", "title_or_message"}:
        return invalid_argument("search_in must be 'title' or 'title_or_message'")

    limit = clamp(args.get("limit"), 100)
    include_announcements = bool(args.get("include_announcements", False))
    only_graded = bool(args.get("only_graded", False))
    exact_title = bool(args.get("exact_title", False))
    search_value = str(args.get("search") or "").strip()
    scan_limit = 300
    client = canvas_client()

    api_search = None if exact_title or looks_like_canvas_id(search_value) else search_value
    api_topics = client.list_discussion_topics(
        course_id=course_id,
        search=api_search or None,
        only_graded=False,
        exact_title=False,
        include_announcements=True,
        search_in=search_in,
        limit=scan_limit,
    )

    assignment_topics: list[dict[str, Any]] = []
    needs_assignment_topics = only_graded or bool(search_value) or not api_topics
    if needs_assignment_topics:
        # ID/alias searches match against ids locally, so the API search_term
        # (which only matches names) must not pre-filter assignments.
        assignment_search = api_search or None
        assignments = client.list_assignments(
            course_id=course_id,
            search=assignment_search,
            include_submission=False,
            include_discussion_topic=True,
            limit=scan_limit,
        )
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
                id_aliases(
                    str(assignment_value) if assignment_value is not None else "",
                    course_id=course_id,
                )
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
        _map_discussion_topic_item(topic, course_id=course_id)
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
        return missing_argument("course_id")
    if not topic_id:
        return missing_argument("topic_id")

    include_replies = bool(args.get("include_replies", True))
    include_participants = bool(args.get("include_participants", True))
    limit = clamp(args.get("limit"), 200)

    context = resolve_discussion_topic_context(course_id, topic_id)

    if context.view is None:
        error = discussion_topic_context_error(
            topic_id=topic_id,
            context=context,
            not_found_message=(
                "Could not resolve a discussion topic from the provided id. "
                "Try list_discussion_topics first and pass its topic id."
            ),
        )
        if error is not None:
            return error
        context.view = {"view": [], "participants": []}

    view = context.view
    canonical_topic = context.canonical_topic
    resolved_topic = context.resolved_topic

    topic_view_id = str(view.get("id", "")).strip()
    if not topic_view_id and isinstance(canonical_topic, dict):
        topic_view_id = str(canonical_topic.get("id") or "").strip()
    if not topic_view_id and isinstance(resolved_topic, dict):
        topic_view_id = str(resolved_topic.get("id") or "").strip()
    if not topic_view_id:
        return tool_error(
            "not_found",
            (
                "Canvas returned an empty discussion payload. "
                "This usually means the id does not map to a discussion topic."
            ),
            topic_id=topic_id,
        )

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
        return tool_error(
            "not_found",
            (
                "Canvas did not return a valid discussion payload for this id. "
                "Pass a discussion topic id from list_discussion_topics."
            ),
            topic_id=topic_id,
        )

    topic_message = truncate_html(
        first_non_none(
            view.get("message"),
            canonical_topic.get("message")
            if isinstance(canonical_topic, dict)
            else None,
            resolved_topic.get("message") if isinstance(resolved_topic, dict) else None,
        )
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
        canonical_topic.get("discussion_type")
        if isinstance(canonical_topic, dict)
        else None,
        resolved_topic.get("discussion_type")
        if isinstance(resolved_topic, dict)
        else None,
    )
    topic_html_url = first_non_none(
        view.get("html_url"),
        canonical_topic.get("html_url") if isinstance(canonical_topic, dict) else None,
        resolved_topic.get("html_url") if isinstance(resolved_topic, dict) else None,
    )

    return {
        "course_id": course_id,
        "requested_topic_id": topic_id,
        "requested_topic_id_aliases": context.topic_candidates,
        "assignment_linked_topic_id": context.assignment_linked_topic_id,
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
