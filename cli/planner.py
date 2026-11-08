from __future__ import annotations

from typing import Annotated

import typer

from cli.output import invoke

planner_app = typer.Typer(help="To Do list (planner) commands. Only changes your own To Do list.")


@planner_app.command("items")
def planner_items(
    start: Annotated[str | None, typer.Option("--start", help="YYYY-MM-DD; defaults to today.")] = None,
    end: Annotated[str | None, typer.Option("--end", help="YYYY-MM-DD.")] = None,
    incomplete: Annotated[bool, typer.Option("--incomplete", help="Only items not done yet.")] = False,
    limit: Annotated[int, typer.Option(help="Maximum items.")] = 100,
) -> None:
    invoke(
        "list_planner_items",
        {"start_date": start, "end_date": end, "incomplete_only": incomplete, "limit": limit},
    )


@planner_app.command("add")
def planner_add(
    title: Annotated[str, typer.Argument(help="What to do.")],
    date: Annotated[str | None, typer.Option("--date", help="YYYY-MM-DD or ISO date-time.")] = None,
    details: Annotated[str | None, typer.Option(help="Notes.")] = None,
    course_id: Annotated[str | None, typer.Option("--course", help="Course to file it under.")] = None,
) -> None:
    invoke(
        "create_todo_note",
        {"title": title, "todo_date": date, "details": details, "course_id": course_id},
    )


@planner_app.command("edit")
def planner_edit(
    note_id: Annotated[str, typer.Argument(help="To-do note ID.")],
    title: Annotated[str | None, typer.Option(help="New title.")] = None,
    date: Annotated[str | None, typer.Option("--date", help="YYYY-MM-DD or ISO date-time.")] = None,
    details: Annotated[str | None, typer.Option(help="New notes.")] = None,
    course_id: Annotated[str | None, typer.Option("--course", help="Course to file it under.")] = None,
) -> None:
    invoke(
        "update_todo_note",
        {"note_id": note_id, "title": title, "todo_date": date, "details": details, "course_id": course_id},
    )


@planner_app.command("delete")
def planner_delete(note_id: Annotated[str, typer.Argument(help="To-do note ID.")]) -> None:
    invoke("delete_todo_note", {"note_id": note_id})


@planner_app.command("done")
def planner_done(
    plannable_type: Annotated[
        str, typer.Argument(help="assignment, quiz, discussion_topic, planner_note, ...")
    ],
    plannable_id: Annotated[str, typer.Argument(help="Its ID, from `planner items`.")],
    undo: Annotated[bool, typer.Option("--undo", help="Mark it not done instead.")] = False,
) -> None:
    invoke(
        "set_todo_item_state",
        {"plannable_type": plannable_type, "plannable_id": plannable_id, "done": not undo},
    )
