from __future__ import annotations

from typing import Any

from tools.common import (
    canvas_client,
    clamp,
    course_tab_target_url,
    id_aliases,
    normalize,
)


def map_course(course: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(course.get("id", "")),
        "name": str(course.get("name", "Untitled course")),
        "course_code": str(course["course_code"])
        if course.get("course_code")
        else None,
        "term_name": str(course["term"]["name"])
        if isinstance(course.get("term"), dict) and course["term"].get("name")
        else None,
        "state": str(course["workflow_state"])
        if course.get("workflow_state")
        else None,
    }


def map_course_tab(tab: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(tab.get("id", "")),
        "label": tab.get("label"),
        "type": tab.get("type"),
        "position": tab.get("position"),
        "hidden": tab.get("hidden"),
        "visibility": tab.get("visibility"),
        "url": tab.get("url"),
        "full_url": tab.get("full_url"),
        "html_url": tab.get("html_url"),
    }


def relevance_score(query: str, course: dict[str, Any]) -> float:
    q = normalize(query)
    if not q:
        return 0.0

    name = normalize(course.get("name"))
    code = normalize(course.get("course_code"))

    if q == name or q == code:
        return 1.0

    score = 0.0
    if code.startswith(q):
        score = max(score, 0.97)
    elif q in code:
        score = max(score, 0.91)

    if name.startswith(q):
        score = max(score, 0.93)
    elif q in name:
        score = max(score, 0.86)

    q_tokens = [token for token in q.split(" ") if token]
    if q_tokens:
        overlap = sum(1 for token in q_tokens if token in name or token in code)
        score = max(score, (overlap / len(q_tokens)) * 0.8)

    return score


def list_courses(args: dict[str, Any]) -> dict[str, Any]:
    favorites_only = bool(args.get("favorites_only", True))
    search = args.get("search")
    limit = clamp(args.get("limit"), 50)
    courses = canvas_client().list_courses(
        favorites_only=favorites_only,
        search=str(search) if search else None,
        limit=limit,
    )
    mapped = [map_course(course) for course in courses]
    return {
        "source": "favorites" if favorites_only else "active-enrollments",
        "count": len(mapped),
        "courses": mapped,
    }


def resolve_course(args: dict[str, Any]) -> dict[str, Any]:
    query = str(args.get("query", "")).strip()
    if not query:
        return {"count": 0, "matches": []}

    favorites_only = bool(args.get("favorites_only", True))
    limit = clamp(args.get("limit"), 5)

    courses = canvas_client().list_courses(
        favorites_only=favorites_only,
        limit=200,
    )
    scored = sorted(
        ({**map_course(course), "score": relevance_score(query, course)} for course in courses),
        key=lambda row: row["score"],
        reverse=True,
    )
    matches = [row for row in scored if row["score"] > 0][:limit]
    return {"count": len(matches), "matches": matches}


def get_course_overview(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    course = canvas_client().get_course(
        course_id=course_id,
        include=["term", "total_students", "teachers", "course_image"],
    )
    teachers = [
        {
            "id": str(teacher.get("id", "")),
            "display_name": teacher.get("display_name"),
            "sortable_name": teacher.get("sortable_name"),
            "avatar_image_url": teacher.get("avatar_image_url"),
            "html_url": teacher.get("html_url"),
        }
        for teacher in (course.get("teachers") or [])
        if isinstance(teacher, dict)
    ]
    return {
        "course": {
            "id": str(course.get("id", "")),
            "name": course.get("name", "Untitled course"),
            "course_code": course.get("course_code"),
            "workflow_state": course.get("workflow_state"),
            "term": course.get("term"),
            "start_at": course.get("start_at"),
            "end_at": course.get("end_at"),
            "time_zone": course.get("time_zone"),
            "default_view": course.get("default_view"),
            "public_syllabus": course.get("public_syllabus"),
            "is_favorite": course.get("is_favorite"),
            "total_students": course.get("total_students"),
            "storage_quota_mb": course.get("storage_quota_mb"),
            "grading_standard_id": course.get("grading_standard_id"),
            "apply_assignment_group_weights": course.get(
                "apply_assignment_group_weights"
            ),
            "hide_final_grades": course.get("hide_final_grades"),
            "html_url": course.get("html_url"),
            "teachers": teachers,
        }
    }


def get_course_syllabus(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    include_body = bool(args.get("include_body", True))
    try:
        body_char_limit = int(args.get("body_char_limit", 12000))
    except (TypeError, ValueError):
        body_char_limit = 12000
    body_char_limit = max(200, min(body_char_limit, 200000))

    course = canvas_client().get_course(
        course_id=course_id,
        include=["syllabus_body", "term", "total_students"],
    )
    syllabus_body = course.get("syllabus_body")
    if not include_body:
        syllabus_body = None
    elif isinstance(syllabus_body, str) and len(syllabus_body) > body_char_limit:
        syllabus_body = syllabus_body[:body_char_limit]

    return {
        "course_id": str(course.get("id", "")) or course_id,
        "course_name": course.get("name", "Untitled course"),
        "course_code": course.get("course_code"),
        "term": course.get("term"),
        "syllabus_body": syllabus_body,
        "has_syllabus_body": bool(course.get("syllabus_body")),
        "syllabus_public": course.get("public_syllabus"),
        "syllabus_raw_length": len(str(course.get("syllabus_body") or "")),
        "html_url": course.get("html_url"),
    }


def list_course_pages(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    published_only = args.get("published_only")
    if published_only is not None:
        published_only = bool(published_only)

    limit = clamp(args.get("limit"), 100)
    pages = canvas_client().list_pages(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        published_only=published_only,
        limit=limit,
    )
    items = [
        {
            "page_id": str(page.get("page_id", "")),
            "url": page.get("url"),
            "title": page.get("title", "Untitled page"),
            "created_at": page.get("created_at"),
            "updated_at": page.get("updated_at"),
            "published": page.get("published"),
            "front_page": page.get("front_page"),
            "hide_from_students": page.get("hide_from_students"),
            "editing_roles": page.get("editing_roles"),
            "html_url": page.get("html_url"),
        }
        for page in pages
    ]
    return {"course_id": course_id, "count": len(items), "pages": items}


def list_course_tabs(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = clamp(args.get("limit"), 100)
    tabs = canvas_client().list_tabs(course_id=course_id, limit=limit)
    items = [map_course_tab(tab) for tab in tabs]
    return {"course_id": course_id, "count": len(items), "tabs": items}


def get_course_tab(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    tab_id = str(args.get("tab_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not tab_id:
        return {"error": "tab_id is required"}

    include_target = bool(args.get("include_target", True))
    tab = canvas_client().get_tab(course_id=course_id, tab_id=tab_id)
    mapped_tab = map_course_tab(tab)

    target = None
    if include_target:
        target_url = course_tab_target_url(tab_id=tab_id, tab=mapped_tab)
        if target_url:
            from tools.misc import resolve_canvas_url

            target = resolve_canvas_url({"url": target_url, "fetch_details": True})

    return {
        "course_id": course_id,
        "tab_id": tab_id,
        "tab": mapped_tab,
        "target": target,
    }


def list_course_people(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    enrollment_types = args.get("enrollment_types")
    if enrollment_types is not None and not isinstance(enrollment_types, list):
        return {"error": "enrollment_types must be an array of strings"}

    limit = clamp(args.get("limit"), 100)
    users = canvas_client().list_course_users(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        enrollment_types=[str(item) for item in enrollment_types]
        if enrollment_types
        else None,
        include_email=bool(args.get("include_email", True)),
        limit=limit,
    )
    people = [
        {
            "id": str(user.get("id", "")),
            "name": user.get("name", "Unknown user"),
            "sortable_name": user.get("sortable_name"),
            "short_name": user.get("short_name"),
            "email": user.get("email"),
            "avatar_url": user.get("avatar_url"),
            "enrollments": [
                {
                    "type": enrollment.get("type"),
                    "role": enrollment.get("role"),
                    "enrollment_state": enrollment.get("enrollment_state"),
                }
                for enrollment in (user.get("enrollments") or [])
                if isinstance(enrollment, dict)
            ],
        }
        for user in users
    ]
    return {"course_id": course_id, "count": len(people), "people": people}
