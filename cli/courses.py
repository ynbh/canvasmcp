from __future__ import annotations

from typing import Annotated, Callable

import typer

course_app = typer.Typer(help="Course-level commands.")


def register(invoke: Callable[[str, dict], None]) -> typer.Typer:
    @course_app.command("overview")
    def course_overview(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")]
    ) -> None:
        invoke("get_course_overview", {"course_id": course_id})

    @course_app.command("syllabus")
    def course_syllabus(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        with_body: Annotated[
            bool,
            typer.Option("--body/--no-body", help="Include syllabus HTML body."),
        ] = True,
        body_char_limit: Annotated[
            int,
            typer.Option(help="Maximum syllabus body characters."),
        ] = 12000,
    ) -> None:
        invoke(
            "get_course_syllabus",
            {
                "course_id": course_id,
                "include_body": with_body,
                "body_char_limit": body_char_limit,
            },
        )

    @course_app.command("context")
    def course_context(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        include_syllabus_body: Annotated[
            bool,
            typer.Option("--body/--no-body", help="Include syllabus body in snapshot."),
        ] = False,
        upcoming_limit: Annotated[
            int, typer.Option(help="Upcoming assignments limit.")
        ] = 20,
        announcements_limit: Annotated[
            int, typer.Option(help="Announcements limit.")
        ] = 10,
        modules_limit: Annotated[int, typer.Option(help="Modules limit.")] = 20,
        module_items_limit: Annotated[
            int, typer.Option(help="Module items limit.")
        ] = 50,
    ) -> None:
        invoke(
            "get_course_context_snapshot",
            {
                "course_id": course_id,
                "include_syllabus_body": include_syllabus_body,
                "upcoming_limit": upcoming_limit,
                "announcements_limit": announcements_limit,
                "modules_limit": modules_limit,
                "module_items_limit": module_items_limit,
            },
        )

    @course_app.command("pages")
    def course_pages(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        search: Annotated[
            str | None, typer.Option(help="Filter by page title/url.")
        ] = None,
        published_only: Annotated[
            bool | None,
            typer.Option(
                "--published",
                help="Only published pages. Omit to include both published and unpublished.",
            ),
        ] = None,
        limit: Annotated[int, typer.Option(help="Maximum number of pages.")] = 100,
    ) -> None:
        invoke(
            "list_course_pages",
            {
                "course_id": course_id,
                "search": search,
                "published_only": published_only,
                "limit": limit,
            },
        )

    @course_app.command("page")
    def course_page(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        url_or_id: Annotated[str, typer.Argument(help="Page URL slug or page ID.")],
        force_as_id: Annotated[
            bool, typer.Option(help="Treat the second argument strictly as a page ID.")
        ] = False,
    ) -> None:
        invoke(
            "canvas_get_page",
            {
                "course_id": course_id,
                "url_or_id": url_or_id,
                "force_as_id": force_as_id,
            },
        )

    @course_app.command("tabs")
    def course_tabs(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        limit: Annotated[int, typer.Option(help="Maximum number of tabs.")] = 100,
    ) -> None:
        invoke("list_course_tabs", {"course_id": course_id, "limit": limit})

    @course_app.command("tab")
    def course_tab(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        tab_id: Annotated[
            str, typer.Argument(help="Tab ID, such as home or modules.")
        ],
        include_target: Annotated[
            bool,
            typer.Option("--target/--no-target", help="Resolve the tab destination."),
        ] = True,
    ) -> None:
        invoke(
            "get_course_tab",
            {
                "course_id": course_id,
                "tab_id": tab_id,
                "include_target": include_target,
            },
        )

    @course_app.command("people")
    def course_people(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        search: Annotated[
            str | None, typer.Option(help="Filter by person name/email.")
        ] = None,
        enrollment_type: Annotated[
            list[str] | None,
            typer.Option("--role", help="Enrollment type filter. Repeat for multiple roles."),
        ] = None,
        include_email: Annotated[
            bool, typer.Option("--email/--no-email", help="Include email addresses.")
        ] = True,
        limit: Annotated[int, typer.Option(help="Maximum number of people.")] = 100,
    ) -> None:
        invoke(
            "list_course_people",
            {
                "course_id": course_id,
                "search": search,
                "enrollment_types": enrollment_type or [],
                "include_email": include_email,
                "limit": limit,
            },
        )

    @course_app.command("modules")
    def course_modules(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        search: Annotated[str | None, typer.Option(help="Filter by module name.")] = None,
        include_items: Annotated[
            bool, typer.Option("--items/--no-items", help="Include module items.")
        ] = False,
        include_content_details: Annotated[
            bool,
            typer.Option(
                "--details/--no-details",
                help="Include Canvas content details for module items.",
            ),
        ] = False,
        limit: Annotated[int, typer.Option(help="Maximum number of modules.")] = 100,
        items_limit: Annotated[
            int, typer.Option(help="Maximum number of items per module.")
        ] = 100,
    ) -> None:
        invoke(
            "list_modules",
            {
                "course_id": course_id,
                "search": search,
                "include_items": include_items,
                "include_content_details": include_content_details,
                "limit": limit,
                "items_limit": items_limit,
            },
        )

    @course_app.command("grades")
    def course_grades(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        student_id: Annotated[str, typer.Option(help="Canvas student ID.")] = "self",
    ) -> None:
        invoke(
            "get_course_grade_summary",
            {"course_id": course_id, "student_id": student_id},
        )

    @course_app.command("submissions")
    def course_submissions(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        student_id: Annotated[str, typer.Option(help="Canvas student ID.")] = "self",
        assignment_id: Annotated[
            list[str] | None,
            typer.Option("--assignment", help="Assignment ID filter. Repeat as needed."),
        ] = None,
        include: Annotated[
            list[str] | None,
            typer.Option("--include", help="Submission include values. Repeat as needed."),
        ] = None,
        grouped: Annotated[
            bool, typer.Option(help="Keep Canvas grouped submission shells.")
        ] = False,
        workflow_state: Annotated[
            str | None, typer.Option(help="Submission workflow state filter.")
        ] = None,
        submitted_since: Annotated[
            str | None, typer.Option(help="ISO datetime lower bound.")
        ] = None,
        graded_since: Annotated[
            str | None, typer.Option(help="ISO datetime lower bound.")
        ] = None,
        limit: Annotated[int, typer.Option(help="Maximum number of submissions.")] = 200,
    ) -> None:
        invoke(
            "list_course_submissions",
            {
                "course_id": course_id,
                "student_id": student_id,
                "assignment_ids": assignment_id or [],
                "include": include or [],
                "grouped": grouped,
                "workflow_state": workflow_state,
                "submitted_since": submitted_since,
                "graded_since": graded_since,
                "limit": limit,
            },
        )

    return course_app
