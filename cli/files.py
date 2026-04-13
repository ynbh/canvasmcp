from __future__ import annotations

from typing import Annotated, Callable

import typer

files_app = typer.Typer(help="File and folder commands.")


def register(invoke: Callable[[str, dict], None]) -> typer.Typer:
    @files_app.command("list")
    def files_list(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        search: Annotated[str | None, typer.Option(help="Filter by file name.")] = None,
        sort: Annotated[str | None, typer.Option(help="Sort key.")] = None,
        order: Annotated[str | None, typer.Option(help="Sort order: asc or desc.")] = None,
        limit: Annotated[int, typer.Option(help="Maximum number of files.")] = 100,
    ) -> None:
        invoke(
            "list_course_files",
            {
                "course_id": course_id,
                "search": search,
                "sort": sort,
                "order": order,
                "limit": limit,
            },
        )

    @files_app.command("download")
    def files_download(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        file_id: Annotated[str, typer.Argument(help="Canvas file ID.")],
        force_refresh: Annotated[
            bool, typer.Option(help="Redownload even if a cached local copy exists.")
        ] = False,
    ) -> None:
        invoke(
            "download_course_file",
            {
                "course_id": course_id,
                "file_id": file_id,
                "force_refresh": force_refresh,
            },
        )

    @files_app.command("folders")
    def files_folders(
        course_id: Annotated[str, typer.Argument(help="Canvas course ID.")],
        limit: Annotated[int, typer.Option(help="Maximum number of folders.")] = 150,
    ) -> None:
        invoke("list_course_folders", {"course_id": course_id, "limit": limit})

    return files_app
