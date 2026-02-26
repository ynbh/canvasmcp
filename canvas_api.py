from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable
import os
import re

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.exceptions import CanvasException
from canvasapi.paginated_list import PaginatedList
from canvasapi.user import User
from canvasapi.util import combine_kwargs

from canvas_urls import canvas_root_url, normalize_canvas_api_base_url

DEFAULT_CANVAS_BASE_URL = "https://canvas.instructure.com"
MAX_PER_PAGE = 100


class CanvasAPIError(RuntimeError):
    pass


def _read_static_canvas_token() -> str:
    return (
        os.getenv("canvas_api_token", "").strip()
        or os.getenv("canvas_api_key", "").strip()
        or os.getenv("CANVAS_API_TOKEN", "").strip()
        or os.getenv("CANVAS_API_KEY", "").strip()
    )


def _read_session_cookies() -> tuple[str, str] | None:
    """Read browser session cookies from environment variables.

    Returns (canvas_session, csrf_token) or None if not configured.
    """
    session_cookie = os.getenv("CANVAS_SESSION_COOKIE", "").strip()
    csrf_token = os.getenv("CANVAS_CSRF_TOKEN", "").strip()
    if session_cookie and csrf_token:
        return session_cookie, csrf_token
    return None


def _is_session_mode() -> bool:
    return os.getenv("CANVAS_AUTH_MODE", "").strip().lower() == "session"


@dataclass(slots=True)
class CanvasClient:
    token_provider: Callable[[], str]
    base_url: str = DEFAULT_CANVAS_BASE_URL
    session_cookies: tuple[str, str] | None = None  # (canvas_session, csrf_token)
    _root_url: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._root_url = canvas_root_url(normalize_canvas_api_base_url(self.base_url))

    @staticmethod
    def _close_canvas(canvas: Canvas) -> None:
        requester = getattr(canvas, "_Canvas__requester", None)
        session = getattr(requester, "_session", None)
        if session is not None:
            session.close()

    def _inject_session_cookies(self, canvas: Canvas) -> None:
        """Replace Bearer token auth with browser session cookies."""
        if not self.session_cookies:
            return
        session_cookie, csrf_token = self.session_cookies
        requester = getattr(canvas, "_Canvas__requester", None)
        if requester is None:
            return
        # Clear the access token so the Bearer header is empty/ignored
        requester.access_token = ""
        # Inject cookies into the underlying requests.Session
        http_session = getattr(requester, "_session", None)
        if http_session is not None:
            from urllib.parse import urlparse
            domain = urlparse(self._root_url).hostname or ""
            http_session.cookies.set("canvas_session", session_cookie, domain=domain)
            http_session.cookies.set("_csrf_token", csrf_token, domain=domain)
            # Add CSRF token as header for non-GET requests
            http_session.headers.update({"X-CSRF-Token": csrf_token})

    def _run_with_canvas(self, call: Callable[[Canvas], Any]) -> Any:
        canvas = Canvas(self._root_url, self.token_provider())
        self._inject_session_cookies(canvas)
        try:
            return call(canvas)
        finally:
            self._close_canvas(canvas)

    def _call_canvas(self, action: Callable[[Canvas], Any], context: str) -> Any:
        try:
            return self._run_with_canvas(action)
        except (CanvasException, TypeError, ValueError) as exc:
            raise CanvasAPIError(
                f"Canvas request failed: {context}. Response: {exc}"
            ) from exc

    @staticmethod
    def _item_to_dict(item: Any) -> dict[str, Any]:
        if isinstance(item, dict):
            return dict(item)

        payload: dict[str, Any] = {}
        for key, value in vars(item).items():
            if key.startswith("_") or key.endswith("_date"):
                continue
            payload[key] = value
        return payload

    @staticmethod
    def _take_limit(items: Iterable[Any], limit: int) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 300))
        out: list[dict[str, Any]] = []
        for item in items:
            out.append(CanvasClient._item_to_dict(item))
            if len(out) >= safe_limit:
                break
        return out

    def _paginate_list(
        self, items: Iterable[Any], *, limit: int = 100
    ) -> list[dict[str, Any]]:
        return self._take_limit(items, limit)

    @staticmethod
    def _custom_paginated_call(
        canvas: Canvas,
        *,
        content_class: type[Any],
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> PaginatedList:
        requester = getattr(canvas, "_Canvas__requester")
        if params:
            return PaginatedList(
                content_class,
                requester,
                "GET",
                endpoint,
                _kwargs=combine_kwargs(**params),
            )
        return PaginatedList(content_class, requester, "GET", endpoint)

    def list_courses(
        self,
        *,
        favorites_only: bool = True,
        search: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            if favorites_only:
                raw = self._custom_paginated_call(
                    canvas,
                    content_class=Course,
                    endpoint="users/self/favorites/courses",
                    params={"include": ["term", "favorites"], "per_page": MAX_PER_PAGE},
                )
            else:
                raw = canvas.get_courses(
                    enrollment_state="active",
                    include=["term", "favorites"],
                    per_page=MAX_PER_PAGE,
                )
            return self._paginate_list(raw, limit=limit)

        courses = self._call_canvas(_load, "list courses")
        if not search:
            return courses

        q = search.casefold()
        return [
            course
            for course in courses
            if q in str(course.get("name", "")).casefold()
            or q in str(course.get("course_code", "")).casefold()
        ]

    def get_course(
        self,
        *,
        course_id: str,
        include: list[str] | None = None,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            params: dict[str, Any] = {}
            if include:
                params["include"] = include
            course = canvas.get_course(course_id, **params)
            return self._item_to_dict(course)

        return self._call_canvas(_load, f"get course {course_id}")

    def list_assignments(
        self,
        *,
        course_id: str,
        search: str | None = None,
        bucket: str | None = None,
        include_submission: bool = False,
        include_discussion_topic: bool = True,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if search:
                params["search_term"] = search
            if bucket:
                params["bucket"] = bucket
            include: list[str] = []
            if include_discussion_topic:
                include.append("discussion_topic")
            if include_submission:
                include.append("submission")
            if include:
                params["include"] = include
            assignments = course.get_assignments(**params)
            return self._paginate_list(assignments, limit=limit)

        return self._call_canvas(_load, f"list assignments for course {course_id}")

    def get_assignment(
        self,
        *,
        course_id: str,
        assignment_id: str,
        include_submission: bool = False,
        include_discussion_topic: bool = True,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {}
            include: list[str] = []
            if include_discussion_topic:
                include.append("discussion_topic")
            if include_submission:
                include.append("submission")
            if include:
                params["include"] = include
            assignment = course.get_assignment(assignment_id, **params)
            return self._item_to_dict(assignment)

        return self._call_canvas(
            _load,
            f"get assignment {assignment_id} for course {course_id}",
        )

    def list_pages(
        self,
        *,
        course_id: str,
        search: str | None = None,
        published_only: bool | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if search:
                params["search_term"] = search
            if published_only is not None:
                params["published"] = published_only
            pages = course.get_pages(**params)
            return self._paginate_list(pages, limit=limit)

        return self._call_canvas(_load, f"list pages for course {course_id}")

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
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
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

    def get_discussion_topic(
        self,
        *,
        course_id: str,
        topic_id: str,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            course = canvas.get_course(course_id)
            topic = course.get_discussion_topic(topic_id)
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
            course = canvas.get_course(course_id)
            return dict(course.get_full_discussion_topic(topic_id))

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
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if search:
                params["search_term"] = search
            if sort:
                params["sort"] = sort
            if order:
                params["order"] = order
            files = course.get_files(**params)
            return self._paginate_list(files, limit=limit)

        return self._call_canvas(_load, f"list files for course {course_id}")

    def get_file(
        self,
        *,
        course_id: str,
        file_id: str,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            course = canvas.get_course(course_id)
            canvas_file = course.get_file(file_id)
            return self._item_to_dict(canvas_file)

        return self._call_canvas(_load, f"get file {file_id} for course {course_id}")

    def download_file(
        self,
        *,
        course_id: str,
        file_id: str,
        destination_path: str,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            course = canvas.get_course(course_id)
            canvas_file = course.get_file(file_id)
            canvas_file.download(destination_path)
            return self._item_to_dict(canvas_file)

        return self._call_canvas(
            _load,
            f"download file {file_id} for course {course_id}",
        )

    def list_assignment_groups(
        self,
        *,
        course_id: str,
        include_assignments: bool = False,
        include_submission: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            include: list[str] = []
            if include_assignments:
                include.append("assignments")
            if include_submission:
                include.append("submission")
            if include:
                params["include"] = include
            groups = course.get_assignment_groups(**params)
            return self._paginate_list(groups, limit=limit)

        return self._call_canvas(
            _load,
            f"list assignment groups for course {course_id}",
        )

    def list_submissions(
        self,
        *,
        course_id: str,
        student_id: str = "self",
        assignment_ids: list[str] | None = None,
        include: list[str] | None = None,
        grouped: bool = False,
        workflow_state: str | None = None,
        submitted_since: str | None = None,
        graded_since: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            effective_include = list(include or [])
            for default_include in (
                "assignment",
                "submission_history",
                "submission_comments",
            ):
                if default_include not in effective_include:
                    effective_include.append(default_include)

            params: dict[str, Any] = {
                "per_page": MAX_PER_PAGE,
            }
            if grouped:
                params["grouped"] = True
            if student_id:
                params["student_ids"] = [student_id]
            if assignment_ids:
                params["assignment_ids"] = assignment_ids
            if effective_include:
                params["include"] = effective_include
            if workflow_state:
                params["workflow_state"] = workflow_state
            if submitted_since:
                params["submitted_since"] = submitted_since
            if graded_since:
                params["graded_since"] = graded_since

            submissions = course.get_multiple_submissions(**params)
            return self._paginate_list(submissions, limit=limit)

        return self._call_canvas(_load, f"list submissions for course {course_id}")

    def list_enrollments(
        self,
        *,
        course_id: str,
        user_id: str | None = None,
        include: list[str] | None = None,
        enrollment_type: list[str] | None = None,
        state: list[str] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            if user_id:
                params["user_id"] = user_id
            if include:
                params["include"] = include
            if enrollment_type:
                params["type"] = enrollment_type
            if state:
                params["state"] = state
            enrollments = course.get_enrollments(**params)
            return self._paginate_list(enrollments, limit=limit)

        return self._call_canvas(_load, f"list enrollments for course {course_id}")

    def list_folders(self, *, course_id: str, limit: int = 150) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            folders = course.get_folders(per_page=MAX_PER_PAGE)
            return self._paginate_list(folders, limit=limit)

        return self._call_canvas(_load, f"list folders for course {course_id}")

    def list_modules(
        self,
        *,
        course_id: str,
        search: str | None = None,
        include_items: bool = False,
        include_content_details: bool = False,
        limit: int = 100,
        items_limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            course = canvas.get_course(course_id)
            params: dict[str, Any] = {"per_page": MAX_PER_PAGE}
            include: list[str] = []
            if include_items:
                include.append("items")
            if include_content_details:
                include.append("content_details")
            if include:
                params["include"] = include

            modules = self._paginate_list(
                course.get_modules(**params),
                limit=300 if search else limit,
            )
            if search:
                query = search.casefold()
                modules = [
                    module
                    for module in modules
                    if query in str(module.get("name", "")).casefold()
                ][: max(1, min(int(limit), 300))]

            if include_items:
                for module in modules:
                    if isinstance(module.get("items"), list):
                        continue
                    module_id = module.get("id")
                    if module_id is None:
                        continue
                    module["items"] = self._paginate_list(
                        course.get_module(module_id).get_module_items(
                            per_page=MAX_PER_PAGE
                        ),
                        limit=items_limit,
                    )
            return modules

        return self._call_canvas(_load, f"list modules for course {course_id}")

    def get_page(
        self,
        *,
        course_id: str,
        url_or_id: str,
        force_as_id: bool = False,
    ) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            course = canvas.get_course(course_id)
            lookup = url_or_id.strip()
            if force_as_id and not lookup.startswith("page_id:"):
                lookup = f"page_id:{lookup}"
            page = course.get_page(lookup)
            return self._item_to_dict(page)

        return self._call_canvas(
            _load,
            f"get page {url_or_id} for course {course_id}",
        )

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
            params: dict[str, Any] = {
                "active_only": active_only,
                "per_page": MAX_PER_PAGE,
            }
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

    def list_course_users(
        self,
        *,
        course_id: str,
        search: str | None = None,
        enrollment_types: list[str] | None = None,
        include_email: bool = True,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            params: dict[str, Any] = {
                "include": ["email", "enrollments"]
                if include_email
                else ["enrollments"],
                "per_page": MAX_PER_PAGE,
            }
            if search:
                params["search_term"] = search
            if enrollment_types:
                params["enrollment_type"] = enrollment_types

            users = self._custom_paginated_call(
                canvas,
                content_class=User,
                endpoint=f"courses/{course_id}/users",
                params=params,
            )
            return self._paginate_list(users, limit=limit)

        return self._call_canvas(_load, f"list users for course {course_id}")


def create_canvas_client_from_env() -> CanvasClient:
    base_url = os.getenv("CANVAS_BASE_URL", DEFAULT_CANVAS_BASE_URL)

    # Session cookie mode: use browser cookies instead of API token
    if _is_session_mode():
        cookies = _read_session_cookies()
        if not cookies:
            raise CanvasAPIError(
                "CANVAS_AUTH_MODE=session but CANVAS_SESSION_COOKIE and/or "
                "CANVAS_CSRF_TOKEN are not set."
            )
        return CanvasClient(
            token_provider=lambda: "session-cookie-auth",  # dummy token
            base_url=base_url,
            session_cookies=cookies,
        )

    static_token = _read_static_canvas_token()
    if static_token:
        return CanvasClient(
            token_provider=lambda: static_token,
            base_url=base_url,
        )

    raise CanvasAPIError(
        "Canvas auth is not configured. Set CANVAS_API_TOKEN "
        "(or CANVAS_API_KEY/canvas_api_token/canvas_api_key), "
        "or set CANVAS_AUTH_MODE=session with CANVAS_SESSION_COOKIE and CANVAS_CSRF_TOKEN."
    )


def ensure_canvas_auth_configured() -> str:
    if _is_session_mode():
        cookies = _read_session_cookies()
        if cookies:
            return "session-cookie"
        raise CanvasAPIError(
            "CANVAS_AUTH_MODE=session but CANVAS_SESSION_COOKIE and/or "
            "CANVAS_CSRF_TOKEN are not set."
        )

    static_token = _read_static_canvas_token()
    if static_token:
        return "api-token"

    raise CanvasAPIError(
        "No Canvas authentication found. Set CANVAS_API_TOKEN "
        "(or CANVAS_API_KEY/canvas_api_token/canvas_api_key), "
        "or set CANVAS_AUTH_MODE=session with CANVAS_SESSION_COOKIE and CANVAS_CSRF_TOKEN."
    )
