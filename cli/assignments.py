from __future__ import annotations

from typing import Annotated, Callable

import typer

assignments_app = typer.Typer(help="Assignment commands.")
submissions_app = typer.Typer(help="Assignment submission commands.")
assignments_app.add_typer(submissions_app, name="submissions")


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

    @submissions_app.command("install")
    def assignments_submissions_install(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        assignment_id: Annotated[str, typer.Argument(help="Assignment ID.")],
        force_refresh: Annotated[
            bool, typer.Option(help="Redownload files even if local copies exist.")
        ] = False,
    ) -> None:
        invoke(
            "install_assignment_submission_files",
            {
                "course_id": course_id,
                "assignment_id": assignment_id,
                "force_refresh": force_refresh,
            },
        )

    @submissions_app.command("preview")
    def assignments_submissions_preview(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        assignment_id: Annotated[str, typer.Argument(help="Assignment ID.")],
        submission_type: Annotated[
            str,
            typer.Option(
                "--type",
                help="Submission type: online_upload or online_text_entry.",
            ),
        ],
        files: Annotated[
            list[str] | None,
            typer.Option("--file", help="Local file to upload. Repeatable."),
        ] = None,
        body: Annotated[
            str | None, typer.Option("--body", help="Text entry body.")
        ] = None,
        submit_at: Annotated[
            str | None,
            typer.Option("--at", help="ISO-8601 submit time with timezone offset."),
        ] = None,
        minutes_before_due: Annotated[
            int | None,
            typer.Option(
                "--minutes-before-due",
                help="Submit this many minutes before due_at (resolved once at preview).",
            ),
        ] = None,
        now: Annotated[
            bool,
            typer.Option(
                "--now",
                help="Submit immediately on confirm (no LaunchAgent).",
            ),
        ] = False,
    ) -> None:
        payload: dict = {
            "course_id": course_id,
            "assignment_id": assignment_id,
            "submission_type": submission_type,
            "now": now,
        }
        if files:
            payload["file_paths"] = files
        if body is not None:
            payload["body"] = body
        if submit_at:
            payload["submit_at"] = submit_at
        if minutes_before_due is not None:
            payload["minutes_before_due"] = minutes_before_due
        invoke("preview_assignment_submission", payload)

    @submissions_app.command("confirm")
    def assignments_submissions_confirm(
        preview_token: Annotated[str, typer.Argument(help="Token from preview.")],
        override: Annotated[
            bool,
            typer.Option(
                "--override",
                help="Cancel the existing pending job for this assignment.",
            ),
        ] = False,
        caffeinate: Annotated[
            bool,
            typer.Option(
                "--caffeinate",
                help="Keep the Mac awake until scheduled fire finishes. Illegal with --now.",
            ),
        ] = False,
    ) -> None:
        invoke(
            "confirm_assignment_submission",
            {
                "preview_token": preview_token,
                "override": override,
                "caffeinate": caffeinate,
            },
        )

    @submissions_app.command("scheduled")
    def assignments_submissions_scheduled(
        status: Annotated[
            str | None,
            typer.Option("--status", help="Filter by job status."),
        ] = None,
    ) -> None:
        payload: dict = {}
        if status:
            payload["status"] = status
        invoke("list_scheduled_submissions", payload)

    @submissions_app.command("status")
    def assignments_submissions_status(
        job_id: Annotated[str, typer.Argument(help="Scheduled job ID.")],
    ) -> None:
        invoke("get_scheduled_submission", {"job_id": job_id})

    @submissions_app.command("cancel")
    def assignments_submissions_cancel(
        job_id: Annotated[str, typer.Argument(help="Scheduled job ID.")],
    ) -> None:
        invoke("cancel_scheduled_submission", {"job_id": job_id})

    return assignments_app
