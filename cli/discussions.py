from __future__ import annotations

from typing import Annotated, Callable

import typer

discussion_app = typer.Typer(help="Discussion commands.")


def register(invoke: Callable[[str, dict], None]) -> typer.Typer:
    @discussion_app.command("list")
    def discussion_list(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        search: Annotated[
            str | None, typer.Option(help="Search title or title/message.")
        ] = None,
        graded_only: Annotated[
            bool, typer.Option("--graded", help="Only include graded discussions.")
        ] = False,
        exact_title: Annotated[
            bool, typer.Option(help="Require exact title match when searching.")
        ] = False,
        include_announcements: Annotated[
            bool, typer.Option(help="Include announcement topics.")
        ] = False,
        search_in: Annotated[
            str,
            typer.Option(help="Search mode: title or title_or_message."),
        ] = "title",
        limit: Annotated[int, typer.Option(help="Maximum number of topics.")] = 100,
    ) -> None:
        invoke(
            "list_discussion_topics",
            {
                "course_id": course_id,
                "search": search,
                "only_graded": graded_only,
                "exact_title": exact_title,
                "include_announcements": include_announcements,
                "search_in": search_in,
                "limit": limit,
            },
        )

    @discussion_app.command("show")
    def discussion_show(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        topic_id: Annotated[str, typer.Argument(help="Discussion topic ID.")],
        include_replies: Annotated[
            bool, typer.Option("--replies/--no-replies", help="Include nested replies.")
        ] = True,
        include_participants: Annotated[
            bool,
            typer.Option(
                "--participants/--no-participants",
                help="Include discussion participant metadata.",
            ),
        ] = True,
        limit: Annotated[int, typer.Option(help="Maximum entries to return.")] = 200,
    ) -> None:
        invoke(
            "get_discussion_entries",
            {
                "course_id": course_id,
                "topic_id": topic_id,
                "include_replies": include_replies,
                "include_participants": include_participants,
                "limit": limit,
            },
        )

    return discussion_app
