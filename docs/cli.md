# Command table

See the [README](../README.md) for install, auth, and the usual flow. `canvas --help` is the source of truth for flags.

## Commands

| Command | Tool |
|---|---|
| `canvas today` | `get_today` |
| `canvas courses` | `list_courses` |
| `canvas resolve QUERY` | `resolve_course` |
| `canvas course overview ID` | `get_course_overview` |
| `canvas course syllabus ID` | `get_course_syllabus` |
| `canvas course context ID` | `get_course_context_snapshot` |
| `canvas assignments list ID` | `list_course_assignments` |
| `canvas assignments show COURSE ASSIGNMENT` | `get_assignment_details` |
| `canvas assignments rubric COURSE ASSIGNMENT` | `get_assignment_rubric` |
| `canvas assignments groups ID` | `list_assignment_groups` |
| `canvas course submissions ID` | `list_course_submissions` |
| `canvas assignments submissions install COURSE ASSIGNMENT` | `install_assignment_submission_files` |
| `canvas assignments submissions preview COURSE ASSIGNMENT` | `preview_assignment_submission` |
| `canvas assignments submissions confirm TOKEN` | `confirm_assignment_submission` |
| `canvas assignments submissions scheduled` | `list_scheduled_submissions` |
| `canvas assignments submissions status JOB` | `get_scheduled_submission` |
| `canvas assignments submissions cancel JOB` | `cancel_scheduled_submission` |
| `canvas course grades ID` | `get_course_grade_summary` |
| `canvas course modules ID` | `list_modules` |
| `canvas discussion list ID` | `list_discussion_topics` |
| `canvas discussion show COURSE TOPIC` | `get_discussion_entries` |
| `canvas course pages ID` | `list_course_pages` |
| `canvas course page COURSE SLUG_OR_ID` | `canvas_get_page` |
| `canvas course tabs ID` | `list_course_tabs` |
| `canvas course tab COURSE TAB` | `get_course_tab` |
| `canvas files list ID` | `list_course_files` |
| `canvas files download COURSE FILE` | `download_course_file` |
| `canvas files folders ID` | `list_course_folders` |
| `canvas announcements --course ID` | `list_announcements` |
| `canvas todo` | `list_todo_items` |
| `canvas course people ID` | `list_course_people` |
| `canvas url URL` | `resolve_canvas_url` |

`canvas_get_page` is wiki pages only. Use `canvas url` when the link type is unknown. Non-self submission queries need extra Canvas permissions.
