from __future__ import annotations

from typing import Annotated

import typer

from cli.output import invoke

inbox_app = typer.Typer(help="Inbox commands (read-only; never marks messages read).")


@inbox_app.command("list")
def inbox_list(
    scope: Annotated[
        str,
        typer.Option(help="inbox, unread, starred, sent, or archived."),
    ] = "inbox",
    course_id: Annotated[
        str | None, typer.Option("--course", help="Only this course's conversations.")
    ] = None,
    limit: Annotated[int, typer.Option(help="Maximum conversations.")] = 50,
) -> None:
    invoke(
        "list_inbox_conversations",
        {"scope": scope, "course_id": course_id, "limit": limit},
    )


@inbox_app.command("show")
def inbox_show(
    conversation_id: Annotated[str, typer.Argument(help="Conversation ID.")],
) -> None:
    invoke("get_inbox_conversation", {"conversation_id": conversation_id})
