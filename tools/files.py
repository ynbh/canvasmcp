from __future__ import annotations

from typing import Any

from tools.common import canvas_client, clamp, download_dir, download_file_path


def list_course_files(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = clamp(args.get("limit"), 100)
    files = canvas_client().list_files(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        sort=str(args.get("sort")) if args.get("sort") else None,
        order=str(args.get("order")) if args.get("order") else None,
        limit=limit,
    )
    items = [
        {
            "id": str(file.get("id", "")),
            "display_name": file.get("display_name"),
            "filename": file.get("filename"),
            "content_type": file.get("content_type"),
            "size": file.get("size"),
            "updated_at": file.get("updated_at"),
            "url": file.get("url"),
            "folder_id": str(file["folder_id"])
            if file.get("folder_id") is not None
            else None,
        }
        for file in files
    ]
    return {"course_id": course_id, "count": len(items), "files": items}


def download_course_file(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    file_id = str(args.get("file_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}
    if not file_id:
        return {"error": "file_id is required"}

    force_refresh = bool(args.get("force_refresh", False))
    root = download_dir()
    root.mkdir(parents=True, exist_ok=True)

    file_info = canvas_client().get_file(course_id=course_id, file_id=file_id)
    display_name = str(
        file_info.get("display_name") or file_info.get("filename") or f"file_{file_id}"
    )
    target_path = download_file_path(root, course_id, file_id, display_name)

    if target_path.exists() and force_refresh:
        target_path.unlink()

    if target_path.exists():
        return {
            "course_id": course_id,
            "file_id": file_id,
            "display_name": display_name,
            "local_path": str(target_path),
            "size_bytes": target_path.stat().st_size,
            "content_type": file_info.get("content_type"),
            "already_present": True,
        }

    downloaded = canvas_client().download_file(
        course_id=course_id,
        file_id=file_id,
        destination_path=str(target_path),
    )
    return {
        "course_id": course_id,
        "file_id": file_id,
        "display_name": display_name,
        "local_path": str(target_path),
        "size_bytes": target_path.stat().st_size,
        "content_type": downloaded.get("content_type"),
        "already_present": False,
    }


def list_course_folders(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = clamp(args.get("limit"), 150)
    folders = canvas_client().list_folders(course_id=course_id, limit=limit)
    items = [
        {
            "id": str(folder.get("id", "")),
            "name": folder.get("name", "Untitled folder"),
            "full_name": folder.get("full_name"),
            "parent_folder_id": str(folder["parent_folder_id"])
            if folder.get("parent_folder_id") is not None
            else None,
            "files_count": folder.get("files_count"),
            "folders_count": folder.get("folders_count"),
            "updated_at": folder.get("updated_at"),
        }
        for folder in folders
    ]
    return {"course_id": course_id, "count": len(items), "folders": items}


def list_modules(args: dict[str, Any]) -> dict[str, Any]:
    course_id = str(args.get("course_id", "")).strip()
    if not course_id:
        return {"error": "course_id is required"}

    limit = clamp(args.get("limit"), 100)
    items_limit = clamp(args.get("items_limit"), 100)
    modules = canvas_client().list_modules(
        course_id=course_id,
        search=str(args.get("search")) if args.get("search") else None,
        include_items=bool(args.get("include_items", False)),
        include_content_details=bool(args.get("include_content_details", False)),
        limit=limit,
        items_limit=items_limit,
    )

    items = []
    for module in modules:
        module_items = []
        if isinstance(module.get("items"), list):
            module_items = [
                {
                    "id": str(item.get("id", "")),
                    "type": item.get("type"),
                    "title": item.get("title"),
                    "page_url": item.get("page_url"),
                    "content_id": str(item["content_id"])
                    if item.get("content_id") is not None
                    else None,
                    "html_url": item.get("html_url"),
                    "url": item.get("url"),
                    "published": item.get("published"),
                    "position": item.get("position"),
                    "completion_requirement": item.get("completion_requirement"),
                    "content_details": item.get("content_details"),
                }
                for item in module["items"]
                if isinstance(item, dict)
            ]

        items.append(
            {
                "id": str(module.get("id", "")),
                "name": module.get("name", "Untitled module"),
                "position": module.get("position"),
                "unlock_at": module.get("unlock_at"),
                "require_sequential_progress": module.get(
                    "require_sequential_progress"
                ),
                "publish_final_grade": module.get("publish_final_grade"),
                "published": module.get("published"),
                "state": module.get("state"),
                "prerequisite_module_ids": [
                    str(module_id)
                    for module_id in (module.get("prerequisite_module_ids") or [])
                ],
                "items_count": module.get("items_count"),
                "items_url": module.get("items_url"),
                "items": module_items,
            }
        )

    return {"course_id": course_id, "count": len(items), "modules": items}
