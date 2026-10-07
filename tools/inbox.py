from __future__ import annotations

from typing import Any

from tools.common import (
    DEFAULT_HTML_CHAR_LIMIT,
    canvas_client,
    clamp,
    invalid_argument,
    looks_like_canvas_id,
    missing_argument,
    truncate_html,
)

INBOX_SCOPES = ("inbox", "unread", "starred", "sent", "archived")
PREVIEW_CHAR_LIMIT = 300


def list_inbox_conversations(args: dict[str, Any]) -> dict[str, Any]:
    scope = str(args.get("scope") or "inbox").strip().lower()
    if scope not in INBOX_SCOPES:
        return invalid_argument(f"scope must be one of: {', '.join(INBOX_SCOPES)}")
    course_id = str(args.get("course_id") or "").strip()
    if course_id and not looks_like_canvas_id(course_id):
        return invalid_argument("course_id must be a Canvas course ID")

    limit = clamp(args.get("limit"), 50)
    conversations = canvas_client().list_conversations(
        scope=None if scope == "inbox" else scope,  # Canvas's default view is the inbox
        course_id=course_id or None,
        limit=limit,
    )
    items = [_map_conversation_summary(item) for item in conversations]
    return {"scope": scope, "course_id": course_id or None, "count": len(items), "conversations": items}


def get_inbox_conversation(args: dict[str, Any]) -> dict[str, Any]:
    conversation_id = str(args.get("conversation_id") or "").strip()
    if not conversation_id:
        return missing_argument("conversation_id")
    if not looks_like_canvas_id(conversation_id):
        return invalid_argument("conversation_id must be a Canvas conversation ID")

    conversation = canvas_client().get_conversation(conversation_id=conversation_id)
    names = _participant_names(conversation)
    messages = [_map_message(message, names) for message in conversation.get("messages") or []]
    return {
        "id": str(conversation.get("id", conversation_id)),
        "subject": conversation.get("subject"),
        "workflow_state": conversation.get("workflow_state"),
        "starred": bool(conversation.get("starred", False)),
        "context_name": conversation.get("context_name"),
        "participants": [{"id": pid, "name": name} for pid, name in names.items()],
        "message_count": len(messages),
        "messages": messages,
        "note": "Messages are newest first. Reading this conversation did not mark it as read.",
    }


def _participant_names(conversation: dict[str, Any]) -> dict[str, str]:
    names: dict[str, str] = {}
    for person in conversation.get("participants") or []:
        if person.get("id") is not None:
            names[str(person["id"])] = person.get("full_name") or person.get("name") or ""
    return names


def _map_conversation_summary(item: dict[str, Any]) -> dict[str, Any]:
    properties = item.get("properties") or []
    return {
        "id": str(item.get("id", "")),
        "subject": item.get("subject"),
        "workflow_state": item.get("workflow_state"),
        "starred": bool(item.get("starred", False)),
        # In the sent view Canvas leaves last_message empty until someone replies; yours is last_authored_message.
        "last_message_at": item.get("last_message_at") or item.get("last_authored_message_at"),
        "last_message_preview": truncate_html(
            item.get("last_message") or item.get("last_authored_message"), limit=PREVIEW_CHAR_LIMIT
        ),
        "message_count": item.get("message_count"),
        "context_name": item.get("context_name"),
        "participants": [
            person.get("full_name") or person.get("name")
            for person in item.get("participants") or []
        ],
        "has_attachments": "attachments" in properties,
    }


def _map_message(message: dict[str, Any], names: dict[str, str]) -> dict[str, Any]:
    author_id = str(message.get("author_id", ""))
    body = message.get("body")
    return {
        "id": str(message.get("id", "")),
        "created_at": message.get("created_at"),
        "author_id": author_id,
        "author": names.get(author_id),
        "body": truncate_html(body),
        "body_truncated": len(body or "") > DEFAULT_HTML_CHAR_LIMIT,
        "generated": bool(message.get("generated", False)),
        # Names and IDs only: Canvas attachment URLs embed an access key.
        "attachments": [
            {
                "id": str(attachment.get("id", "")),
                "display_name": attachment.get("display_name"),
                "content_type": attachment.get("content-type") or attachment.get("content_type"),
                "size": attachment.get("size"),
            }
            for attachment in message.get("attachments") or []
        ],
    }
