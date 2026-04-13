from __future__ import annotations

import re
from typing import Any

from canvasapi import Canvas

from auth import CanvasAPIError
from .base import MAX_PER_PAGE


class CanvasContentMixin:
    def list_discussion_topics(
        self,
        *,
        course_id: str,
        search: str | None = None,
        only_graded: bool = False,
        exact_title: bool = False,
        include_announcements: bool = False,
        search_in: str = "title",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _id_aliases(raw: Any) -> set[str]:
            value = str(raw or "").strip()
            if not value:
                return set()
            aliases = {value}
            tilde_match = re.fullmatch(r"(\d+)~(\d+)", value)
            if tilde_match:
                aliases.add(f"{tilde_match.group(1)}000000{tilde_match.group(2)}")
            full_match = re.fullmatch(r"(\d+)000000(\d+)", value)
            if full_match:
                aliases.add(f"{full_match.group(1)}~{full_match.group(2)}")
                aliases.add(full_match.group(2))
            return aliases

        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            topics = self._paginate_list(
                course.get_discussion_topics(
                    only_announcements=False,
                    per_page=MAX_PER_PAGE,
                ),
                limit=300 if (search or only_graded or exact_title) else limit,
            )
            if not include_announcements:
                topics = [
                    topic
                    for topic in topics
                    if not (
                        topic.get("announcement")
                        or topic.get("is_announcement")
                        or str(topic.get("discussion_type", "")).casefold()
                        == "announcement"
                    )
                ]

            if search:
                query = search.casefold().strip()
                query_aliases = _id_aliases(search)
                if exact_title:
                    topics = [
                        topic
                        for topic in topics
                        if str(topic.get("title", "")).casefold().strip() == query
                        or bool(
                            query_aliases
                            & (
                                _id_aliases(topic.get("id"))
                                | _id_aliases(topic.get("assignment_id"))
                            )
                        )
                    ]
                elif search_in == "title_or_message":
                    topics = [
                        topic
                        for topic in topics
                        if query in str(topic.get("title", "")).casefold()
                        or query in str(topic.get("message", "")).casefold()
                        or bool(
                            query_aliases
                            & (
                                _id_aliases(topic.get("id"))
                                | _id_aliases(topic.get("assignment_id"))
                            )
                        )
                    ]
                else:
                    topics = [
                        topic
                        for topic in topics
                        if query in str(topic.get("title", "")).casefold()
                        or bool(
                            query_aliases
                            & (
                                _id_aliases(topic.get("id"))
                                | _id_aliases(topic.get("assignment_id"))
                            )
                        )
                    ]

            if only_graded:
                topics = [topic for topic in topics if topic.get("assignment_id")]

            return topics[: max(1, min(int(limit), 300))]

        return self._call_canvas(
            _load,
            f"list discussion topics for course {course_id}",
        )

    def get_discussion_topic(self, *, course_id: str, topic_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            topic = canvas.get_course(course_id).get_discussion_topic(topic_id)
            return self._item_to_dict(topic)

        return self._call_canvas(
            _load,
            f"get discussion topic {topic_id} for course {course_id}",
        )

    def get_discussion_topic_view(
        self,
        *,
        course_id: str,
        topic_id: str,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            return dict(canvas.get_course(course_id).get_full_discussion_topic(topic_id))

        return self._call_canvas(
            _load,
            f"get discussion topic view {topic_id} for course {course_id}",
        )

    def list_files(
        self,
        *,
        course_id: str,
        search: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if search:
                params["search_term"] = search
            if sort:
                params["sort"] = sort
            if order:
                params["order"] = order
            files = canvas.get_course(course_id).get_files(**params)
            return self._paginate_list(files, limit=limit)

        return self._call_canvas(_load, f"list files for course {course_id}")

    def get_file(self, *, course_id: str, file_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            file_info = canvas.get_course(course_id).get_file(file_id)
            return self._item_to_dict(file_info)

        return self._call_canvas(_load, f"get file {file_id} for course {course_id}")

    def download_file(
        self,
        *,
        course_id: str,
        file_id: str,
        destination_path: str,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            file_info = canvas.get_course(course_id).get_file(file_id)
            file_info.download(destination_path)
            return self._item_to_dict(file_info)

        return self._call_canvas(
            _load,
            f"download file {file_id} for course {course_id}",
        )

    def list_folders(self, *, course_id: str, limit: int = 150) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            folders = canvas.get_course(course_id).get_folders(per_page=MAX_PER_PAGE)
            return self._paginate_list(folders, limit=limit)

        return self._call_canvas(_load, f"list folders for course {course_id}")

    def list_announcements(
        self,
        *,
        course_ids: list[str],
        start_date: str | None = None,
        end_date: str | None = None,
        active_only: bool = True,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        if not course_ids:
            raise CanvasAPIError("course_ids is required")

        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {"active_only": active_only, "per_page": MAX_PER_PAGE}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            announcements = canvas.get_announcements(course_ids, **params)
            return self._paginate_list(announcements, limit=limit)

        return self._call_canvas(_load, "list announcements")

    def list_calendar_events(
        self,
        *,
        course_ids: list[str] | None = None,
        event_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        all_events: bool | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if course_ids:
                params["context_codes"] = course_ids
            if event_type and event_type != "both":
                params["type"] = event_type
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if all_events is not None:
                params["all_events"] = all_events
            events = canvas.get_calendar_events(**params)
            return self._paginate_list(events, limit=limit)

        return self._call_canvas(_load, "list calendar events")
