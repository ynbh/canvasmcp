from __future__ import annotations

from typing import Annotated, Callable

import typer

assignments_app = typer.Typer(help="Assignment commands.")


def register(invoke: Callable[[str, dict], None]) -> typer.Typer:
    @assignments_app.command("list")
    def assignments_list(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        search: Annotated[
            str | None, typer.Option(help="Filter by assignment name.")
        ] = None,
        bucket: Annotated[
            str | None, typer.Option(help="Bucket: upcoming, overdue, past, etc.")
        ] = None,
        include_submission: Annotated[
            bool,
            typer.Option(help="Include current user's submission where available."),
        ] = False,
        limit: Annotated[int, typer.Option(help="Maximum number of assignments.")] = 100,
    ) -> None:
        invoke(
            "list_course_assignments",
            {
                "course_id": course_id,
                "search": search,
                "bucket": bucket,
                "include_submission": include_submission,
                "limit": limit,
            },
        )

    @assignments_app.command("show")
    def assignments_show(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        assignment_id: Annotated[str, typer.Argument(help="Assignment ID.")],
        include_submission: Annotated[
            bool,
            typer.Option(help="Include current user's submission where available."),
        ] = False,
    ) -> None:
        invoke(
            "get_assignment_details",
            {
                "course_id": course_id,
                "assignment_id": assignment_id,
                "include_submission": include_submission,
            },
        )

    @assignments_app.command("rubric")
    def assignments_rubric(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        assignment_id: Annotated[str, typer.Argument(help="Assignment ID.")],
        include_assessment: Annotated[
            bool,
            typer.Option(
                help="Include current user's rubric assessment when available."
            ),
        ] = False,
    ) -> None:
        invoke(
            "get_assignment_rubric",
            {
                "course_id": course_id,
                "assignment_id": assignment_id,
                "include_assessment": include_assessment,
            },
        )

    @assignments_app.command("groups")
    def assignments_groups(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        include_assignments: Annotated[
            bool,
            typer.Option("--assignments/--no-assignments", help="Include assignments."),
        ] = False,
        include_submission: Annotated[
            bool, typer.Option(help="Include submission data when available.")
        ] = False,
        limit: Annotated[int, typer.Option(help="Maximum number of groups.")] = 100,
    ) -> None:
        invoke(
            "list_assignment_groups",
            {
                "course_id": course_id,
                "include_assignments": include_assignments,
                "include_submission": include_submission,
                "limit": limit,
            },
        )

    return assignments_app
