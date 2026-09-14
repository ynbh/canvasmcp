"""Scheduled-submit infrastructure (store, launchd, caffeinate, notify, fire).

Agent C (tools/submit.py, cli/assignments.py) should import:

    from schedule.store import (
        PREVIEW_TTL,
        consume_preview,
        create_job,
        get_job,
        get_pending_job,
        list_jobs,
        load_preview,
        parse_submit_at,
        save_preview,
        update_job,
    )
    from schedule.launchd import bootout_job, install_job, plist_label, write_plist
    from schedule.caffeinate import start_caffeinate, stop_caffeinate
    from schedule.notify import notify
    from schedule.fire import cancel_job, fire_job

``cancel_job`` only disarms locally (bootout, stop caffeinate, mark cancelled).
Delete uploaded Canvas files with ``client.delete_user_file`` after cancel.
``fire_job`` is CLI/launchd only — do not register it as an MCP tool.
"""
