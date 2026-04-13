from __future__ import annotations

from typing import Any

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.user import User

from auth import CanvasAPIError
from .base import MAX_PER_PAGE


class CanvasCoursesMixin:
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
            return self._paginate_list(course.get_pages(**params), limit=limit)

        return self._call_canvas(_load, f"list pages for course {course_id}")

    def list_tabs(self, *, course_id: str, limit: int = 100) -> list[dict[str, Any]]:
        def _load(canvas: Canvas) -> list[dict[str, Any]]:
            return self._paginate_list(canvas.get_course(course_id).get_tabs(), limit=limit)

        return self._call_canvas(_load, f"list tabs for course {course_id}")

    def get_tab(self, *, course_id: str, tab_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            course = canvas.get_course(course_id)
            for tab in course.get_tabs():
                data = self._item_to_dict(tab)
                if str(data.get("id", "")).strip() == tab_id:
                    return data
            raise CanvasAPIError(f"Tab '{tab_id}' was not found for this course")

        return self._call_canvas(_load, f"get tab {tab_id} for course {course_id}")

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
            lookup = url_or_id.strip()
            if force_as_id and not lookup.startswith("page_id:"):
                lookup = f"page_id:{lookup}"
            page = canvas.get_course(course_id).get_page(lookup)
            return self._item_to_dict(page)

        return self._call_canvas(_load, f"get page {url_or_id} for course {course_id}")

    def get_front_page(self, *, course_id: str) -> dict[str, Any]:
        def _load(canvas: Canvas) -> dict[str, Any]:
            page = canvas.get_course(course_id).show_front_page()
            return self._item_to_dict(page)

        return self._call_canvas(_load, f"get front page for course {course_id}")

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
