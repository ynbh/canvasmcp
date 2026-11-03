from __future__ import annotations

from unittest import mock


class TestListCoursesTool:
    """Tests for list_courses tool handler."""

    def test_returns_mapped_courses(self, mock_client):
        mock_client.list_courses.return_value = [
            {
                "id": 123,
                "name": "Math 101",
                "course_code": "MATH101",
                "workflow_state": "active",
            },
        ]
        from tools import list_courses

        result = list_courses({"favorites_only": True, "limit": 10})
        assert result["courses"][0].items() >= {
            "id": "123", "name": "Math 101", "course_code": "MATH101", "state": "active"
        }.items()
        mock_client.list_courses.assert_called_once_with(
            favorites_only=True, search=None, limit=10
        )

class TestResolveCourseTool:
    """Tests for resolve_course tool handler."""

    def test_empty_query_returns_no_matches_without_calling_canvas(self, mock_client):
        mock_client.list_courses.return_value = [{"id": 1, "name": "CMSC430"}]
        from tools import resolve_course

        assert resolve_course({"query": "  "}) == {"count": 0, "matches": []}
        mock_client.list_courses.assert_not_called()

    def test_ranks_matches_best_first_and_drops_non_matches(self, mock_client):
        mock_client.list_courses.return_value = [
            {"id": 3, "name": "ENGL101", "course_code": "ENGL101"},
            {"id": 2, "name": "CMSC430 Lab", "course_code": "CMSC430L"},
            {"id": 1, "name": "CMSC430", "course_code": "CMSC430"},
        ]
        from tools import resolve_course

        result = resolve_course({"query": "CMSC430"})

        assert [(m["id"], m["score"]) for m in result["matches"]] == [("1", 1.0), ("2", 0.97)]
        assert result["count"] == 2


class TestListCourseAssignmentsTool:
    """Tests for list_course_assignments tool handler."""

    def test_returns_assignments(self, mock_client):
        mock_client.list_assignments.return_value = [
            {
                "id": 42,
                "name": "HW1",
                "due_at": "2026-03-01",
                "submission_types": ["online_upload"],
            },
        ]
        from tools import list_course_assignments

        result = list_course_assignments({"course_id": "123"})
        assert result["assignments"][0].items() >= {
            "id": "42", "name": "HW1", "due_at": "2026-03-01",
            "submission_types": ["online_upload"],
        }.items()
        assert mock_client.list_assignments.call_args.kwargs["course_id"] == "123"


class TestGetAssignmentDetailsTool:
    """Tests for get_assignment_details tool handler."""

    def test_returns_details(self, mock_client):
        mock_client.get_assignment.return_value = {
            "id": 42,
            "name": "Midterm",
            "description": "<p>Exam</p>",
            "points_possible": 100,
            "rubric": [{"id": "crit1", "description": "Correctness", "points": 10}],
            "rubric_settings": {"points_possible": 10},
        }
        from tools import get_assignment_details

        result = get_assignment_details({"course_id": "1", "assignment_id": "42"})
        assert result["assignment"].items() >= {
            "id": "42",
            "name": "Midterm",
            "description": "<p>Exam</p>",
            "points_possible": 100,
            "has_rubric": True,
            "rubric": [{"id": "crit1", "description": "Correctness", "points": 10}],
            "rubric_settings": {"points_possible": 10},
        }.items()


class TestGetAssignmentRubricTool:
    """Tests for get_assignment_rubric tool handler."""

    def test_returns_rubric(self, mock_client):
        mock_client.get_assignment.return_value = {
            "id": 42,
            "name": "Essay",
            "points_possible": 15,
            "rubric": [
                {
                    "id": "crit1",
                    "description": "Thesis",
                    "points": 5,
                    "ratings": [{"description": "Full marks", "points": 5}],
                }
            ],
            "rubric_settings": {"title": "Essay rubric"},
            "use_rubric_for_grading": True,
        }
        from tools import get_assignment_rubric

        result = get_assignment_rubric({"course_id": "1", "assignment_id": "42"})

        assert result["assignment_name"] == "Essay"
        assert result["criteria_count"] == 1
        assert result["rubric_settings"]["title"] == "Essay rubric"
        mock_client.get_assignment.assert_called_once_with(
            course_id="1",
            assignment_id="42",
            include_submission=False,
            include_discussion_topic=False,
        )

    def test_can_return_current_user_assessment(self, mock_client):
        mock_client.get_assignment.return_value = {
            "id": 42,
            "name": "Essay",
            "rubric": [],
            "submission": {
                "rubric_assessment": {
                    "crit1": {"points": 4, "comments": "Good support"}
                }
            },
        }
        from tools import get_assignment_rubric

        result = get_assignment_rubric(
            {"course_id": "1", "assignment_id": "42", "include_assessment": True}
        )

        assert result["rubric_assessment"]["crit1"]["points"] == 4
        assert result["assessment_source"] == "assignment_submission"
        mock_client.list_submissions.assert_not_called()

    def test_uses_submissions_api_for_missing_assignment_assessment(self, mock_client):
        mock_client.get_assignment.return_value = {
            "id": 42,
            "name": "Essay",
            "rubric": [],
        }
        mock_client.list_submissions.return_value = [
            {"rubric_assessment": {"crit1": {"points": 3}}}
        ]
        from tools import get_assignment_rubric

        result = get_assignment_rubric(
            {"course_id": "1", "assignment_id": "42", "include_assessment": True}
        )

        assert result["rubric_assessment"]["crit1"]["points"] == 3
        assert result["assessment_source"] == "submissions_api"
        mock_client.list_submissions.assert_called_once_with(
            course_id="1",
            student_id="self",
            assignment_ids=["42"],
            include=["rubric_assessment"],
            grouped=False,
            limit=1,
        )

    def test_rubric_assessment_submission_lookup_uses_raw_assignment_id(
        self, mock_client
    ):
        mock_client.get_assignment.return_value = {
            "id": "13980000007438508",
            "name": "Essay",
            "rubric": [],
        }
        mock_client.list_submissions.return_value = [
            {"rubric_assessment": {"crit1": {"points": 3}}}
        ]
        from tools import get_assignment_rubric

        get_assignment_rubric(
            {
                "course_id": "1398466",
                "assignment_id": "1398~7438508",
                "include_assessment": True,
            }
        )

        assert mock_client.list_submissions.call_args.kwargs["assignment_ids"] == [
            "7438508"
        ]


class TestInstallAssignmentSubmissionFilesTool:
    def test_no_submission_returns_message(self, mock_client):
        mock_client.list_submissions.return_value = []
        from tools import install_assignment_submission_files

        result = install_assignment_submission_files(
            {"course_id": "1", "assignment_id": "42"}
        )

        assert result["count"] == 0
        assert result["message"] == "No submission was returned for this assignment."

    def test_uses_raw_assignment_id_for_submission_lookup(self, mock_client):
        mock_client.list_submissions.return_value = []
        from tools import install_assignment_submission_files

        install_assignment_submission_files(
            {"course_id": "1398466", "assignment_id": "1398~7438508"}
        )

        mock_client.list_submissions.assert_called_once_with(
            course_id="1398466",
            student_id="self",
            assignment_ids=["7438508"],
            include=None,
            grouped=False,
            limit=1,
        )

    def test_course_submissions_uses_raw_assignment_ids(self, mock_client):
        mock_client.list_submissions.return_value = []
        from tools import list_course_submissions

        list_course_submissions(
            {
                "course_id": "1398466",
                "assignment_ids": ["1398~7438508", "13980000007438509"],
            }
        )

        mock_client.list_submissions.assert_called_once()
        assert mock_client.list_submissions.call_args.kwargs["assignment_ids"] == [
            "7438508",
            "7438509",
        ]

    def test_no_attachments_returns_message(self, mock_client):
        mock_client.list_submissions.return_value = [{"id": 7, "attachments": []}]
        from tools import install_assignment_submission_files

        result = install_assignment_submission_files(
            {"course_id": "1", "assignment_id": "42"}
        )

        assert result["submission_id"] == "7"
        assert result["count"] == 0
        assert "no attachment" in result["message"]

    def test_downloads_attachment_with_file_id(self, mock_client, tmp_path):
        mock_client.list_submissions.return_value = [
            {"id": 7, "attachments": [{"id": 55, "display_name": "report.pdf"}]}
        ]
        mock_client.get_file.return_value = {
            "id": 55,
            "display_name": "report.pdf",
            "content_type": "application/pdf",
        }

        def download_file(**kwargs):
            path = kwargs["destination_path"]
            with open(path, "wb") as handle:
                handle.write(b"pdf")
            return {"content_type": "application/pdf"}

        mock_client.download_file.side_effect = download_file

        with mock.patch("tools.submissions.download_dir", return_value=tmp_path):
            from tools import install_assignment_submission_files

            result = install_assignment_submission_files(
                {"course_id": "1", "assignment_id": "42"}
            )

        assert result["downloaded_count"] == 1
        assert result["already_present_count"] == 0
        assert result["files"][0]["status"] == "downloaded"
        assert result["files"][0]["size_bytes"] == 3
        mock_client.download_file.assert_called_once()

    def test_downloads_canvasapi_file_attachment_object(self, mock_client, tmp_path):
        class Attachment:
            def __init__(self):
                self.id = 55
                self.display_name = "report.pdf"
                self.filename = "report.pdf"
                self._requester = object()
                self.updated_at_date = object()

            def download(self, destination_path):
                with open(destination_path, "wb") as handle:
                    handle.write(b"pdf")

        attachment = Attachment()
        mock_client.list_submissions.return_value = [
            {"id": 7, "attachments": [attachment]}
        ]

        with mock.patch("tools.submissions.download_dir", return_value=tmp_path):
            from tools import install_assignment_submission_files

            result = install_assignment_submission_files(
                {"course_id": "1", "assignment_id": "42"}
            )

        assert result["downloaded_count"] == 1
        assert result["files"][0]["file_id"] == "55"
        mock_client.get_file.assert_not_called()
        mock_client.download_file.assert_not_called()

    def test_existing_file_is_already_present_without_force(self, mock_client, tmp_path):
        mock_client.list_submissions.return_value = [
            {"id": 7, "attachments": [{"id": 55, "display_name": "report.pdf"}]}
        ]
        mock_client.get_file.return_value = {
            "id": 55,
            "display_name": "report.pdf",
            "content_type": "application/pdf",
        }
        target_dir = tmp_path / "course-1_assignment-42"
        target_dir.mkdir()
        target = target_dir / "submission-7_file-55_report.pdf"
        target.write_bytes(b"cached")

        with mock.patch("tools.submissions.download_dir", return_value=tmp_path):
            from tools import install_assignment_submission_files

            result = install_assignment_submission_files(
                {"course_id": "1", "assignment_id": "42"}
            )

        assert result["already_present_count"] == 1
        assert result["files"][0]["already_present"] is True
        mock_client.download_file.assert_not_called()

    def test_force_refresh_redownloads_existing_file(self, mock_client, tmp_path):
        mock_client.list_submissions.return_value = [
            {"id": 7, "attachments": [{"id": 55, "display_name": "report.pdf"}]}
        ]
        mock_client.get_file.return_value = {
            "id": 55,
            "display_name": "report.pdf",
            "content_type": "application/pdf",
        }
        target_dir = tmp_path / "course-1_assignment-42"
        target_dir.mkdir()
        target = target_dir / "submission-7_file-55_report.pdf"
        target.write_bytes(b"cached")

        def download_file(**kwargs):
            with open(kwargs["destination_path"], "wb") as handle:
                handle.write(b"new")
            return {"content_type": "application/pdf"}

        mock_client.download_file.side_effect = download_file

        with mock.patch("tools.submissions.download_dir", return_value=tmp_path):
            from tools import install_assignment_submission_files

            result = install_assignment_submission_files(
                {"course_id": "1", "assignment_id": "42", "force_refresh": True}
            )

        assert result["downloaded_count"] == 1
        assert target.read_bytes() == b"new"

    def test_skips_attachment_without_file_id(self, mock_client, tmp_path):
        attachment = {"display_name": "report.pdf", "url": "https://example.test/file"}
        mock_client.list_submissions.return_value = [
            {"id": 7, "attachments": [attachment]}
        ]

        with mock.patch("tools.submissions.download_dir", return_value=tmp_path):
            from tools import install_assignment_submission_files

            result = install_assignment_submission_files(
                {"course_id": "1", "assignment_id": "42"}
            )

        assert result["skipped_count"] == 1
        assert result["skipped"][0]["reason"] == "missing_file_id"
        mock_client.download_file.assert_not_called()

    def test_reports_download_errors_and_continues(self, mock_client, tmp_path):
        mock_client.list_submissions.return_value = [
            {
                "id": 7,
                "attachments": [
                    {"id": 55, "display_name": "bad.pdf"},
                    {"id": 56, "display_name": "good.pdf"},
                ],
            }
        ]
        mock_client.get_file.side_effect = [
            {"id": 55, "display_name": "bad.pdf"},
            {"id": 56, "display_name": "good.pdf"},
        ]

        def download_file(**kwargs):
            if kwargs["file_id"] == "55":
                raise RuntimeError("download failed")
            with open(kwargs["destination_path"], "wb") as handle:
                handle.write(b"ok")
            return {"content_type": "application/pdf"}

        mock_client.download_file.side_effect = download_file

        with mock.patch("tools.submissions.download_dir", return_value=tmp_path):
            from tools import install_assignment_submission_files

            result = install_assignment_submission_files(
                {"course_id": "1", "assignment_id": "42"}
            )

        assert result["downloaded_count"] == 1
        assert result["error_count"] == 1
        assert result["errors"][0]["file_id"] == "55"

class TestListCourseFilesTool:
    """Tests for list_course_files tool handler."""

    def test_returns_files(self, mock_client):
        mock_client.list_files.return_value = [
            {
                "id": 1,
                "display_name": "notes.pdf",
                "content_type": "application/pdf",
                "size": 1024,
            },
        ]
        from tools import list_course_files

        result = list_course_files({"course_id": "123"})
        assert result["files"][0].items() >= {
            "id": "1", "display_name": "notes.pdf", "content_type": "application/pdf", "size": 1024
        }.items()
        assert mock_client.list_files.call_args.kwargs["course_id"] == "123"


class TestListCoursePagesTool:
    """Tests for list_course_pages tool handler."""

    def test_returns_pages(self, mock_client):
        mock_client.list_pages.return_value = [
            {"page_id": 1, "url": "home", "title": "Home Page", "published": True},
        ]
        from tools import list_course_pages

        result = list_course_pages({"course_id": "123"})
        assert result["pages"][0].items() >= {
            "page_id": "1", "url": "home", "title": "Home Page", "published": True
        }.items()
        assert mock_client.list_pages.call_args.kwargs["course_id"] == "123"


class TestListCourseTabsTool:
    """Tests for list_course_tabs tool handler."""

    def test_returns_tabs(self, mock_client):
        mock_client.list_tabs.return_value = [
            {
                "id": "home",
                "label": "Home",
                "html_url": "https://umd.instructure.com/courses/123",
            },
            {
                "id": "syllabus",
                "label": "Syllabus",
                "html_url": "https://umd.instructure.com/courses/123/assignments/syllabus",
            },
        ]
        from tools import list_course_tabs

        result = list_course_tabs({"course_id": "123"})
        assert [
            {key: tab[key] for key in ("id", "label", "html_url")} for tab in result["tabs"]
        ] == mock_client.list_tabs.return_value
        assert mock_client.list_tabs.call_args.kwargs["course_id"] == "123"


class TestGetCourseTabTool:
    """Tests for get_course_tab tool handler."""

    def test_returns_tab_with_target(self, mock_client):
        mock_client.get_tab.return_value = {
            "id": "syllabus",
            "label": "Syllabus",
            "html_url": "https://umd.instructure.com/courses/123/assignments/syllabus",
        }
        mock_client.get_course.return_value = {
            "id": 123,
            "name": "Course",
            "course_code": "C",
            "term": {},
            "public_syllabus": False,
            "syllabus_body": "<p>Hello</p>",
            "html_url": "https://umd.instructure.com/courses/123",
        }
        from tools import get_course_tab

        result = get_course_tab({"course_id": "123", "tab_id": "syllabus"})
        assert result["tab"]["id"] == "syllabus"
        assert result["target"]["resource_type"] == "syllabus"


class TestListDiscussionTopicsTool:
    """Tests for list_discussion_topics tool handler."""

    def test_returns_topics(self, mock_client):
        mock_client.list_discussion_topics.return_value = [
            {"id": 10, "title": "Week 1 Discussion", "assignment_id": 42},
        ]
        mock_client.list_assignments.return_value = []
        from tools import list_discussion_topics

        result = list_discussion_topics({"course_id": "123"})
        assert result["topics"][0].items() >= {
            "id": "10", "title": "Week 1 Discussion", "assignment_id": "42"
        }.items()

    def test_merges_assignment_linked_topics_when_discussion_list_empty(
        self, mock_client
    ):
        mock_client.list_discussion_topics.return_value = []
        mock_client.list_assignments.return_value = [
            {
                "id": 77,
                "name": "Prompt Discussion",
                "submission_types": ["discussion_topic"],
                "discussion_topic_id": 99,
                "discussion_topic": {
                    "id": 99,
                    "title": "Prompt Discussion",
                    "message": "<p>Discuss</p>",
                    "html_url": "https://umd.instructure.com/courses/123/discussion_topics/99",
                },
            }
        ]
        from tools import list_discussion_topics

        result = list_discussion_topics({"course_id": "123"})
        assert result["count"] == 1
        assert result["topics"][0]["id"] == "99"
        assert result["topics"][0]["source"] == "assignment_linked"


class TestListAnnouncementsTool:
    """Tests for list_announcements tool handler."""

    def test_returns_announcements(self, mock_client):
        mock_client.list_announcements.return_value = [
            {"id": 5, "title": "Welcome!", "message": "<p>Hi</p>"},
        ]
        from tools import list_announcements

        result = list_announcements({"course_ids": ["123"]})
        assert result["announcements"] == [
            {
                "id": "5",
                "title": "Welcome!",
                "posted_at": None,
                "context_code": None,
                "html_url": None,
                "message": "<p>Hi</p>",
            }
        ]


class TestListTodoItemsTool:
    """Tests for list_todo_items tool handler."""

    def test_returns_todo_items(self, mock_client):
        mock_client.list_todo_items.return_value = [
            {
                "type": "submitting",
                "course_id": 123,
                "context_name": "MATH101",
                "assignment": {"id": 1, "name": "Midterm", "due_at": "2026-04-29"},
            },
        ]
        from tools import list_todo_items

        result = list_todo_items({})
        todo = result["todo"][0]
        assert todo.items() >= {
            "type": "submitting", "course_id": "123", "context_name": "MATH101"
        }.items()
        assert todo["assignment"].items() >= {
            "id": "1", "name": "Midterm", "due_at": "2026-04-29"
        }.items()


class TestListCoursePeopleTool:
    """Tests for list_course_people tool handler."""

    def test_returns_people(self, mock_client):
        mock_client.list_course_users.return_value = [
            {"id": 1, "name": "Jane Doe", "email": "jane@umd.edu", "enrollments": []},
        ]
        from tools import list_course_people

        result = list_course_people({"course_id": "123"})
        assert result["people"][0].items() >= {
            "id": "1", "name": "Jane Doe", "email": "jane@umd.edu", "enrollments": []
        }.items()
        assert mock_client.list_course_users.call_args.kwargs["course_id"] == "123"


class TestResolveCanvasUrlTool:
    """Tests for resolve_canvas_url tool handler."""

    def test_parses_assignment_url(self, mock_client):
        from tools import resolve_canvas_url

        mock_client.get_assignment.return_value = {
            "id": 42,
            "name": "HW1",
            "html_url": "...",
            "due_at": None,
            "points_possible": 10,
        }

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123/assignments/42",
                "fetch_details": True,
            }
        )
        assert result["resource_type"] == "assignment"
        assert result["recommended_tool"] == "get_assignment_details"
        assert mock_client.get_assignment.call_args.kwargs["assignment_id"] == "42"
        assert mock_client.get_assignment.call_args.kwargs["course_id"] == "123"

    def test_parses_discussion_url(self, mock_client):
        from tools import resolve_canvas_url

        mock_client.get_discussion_topic_view.return_value = {
            "id": 10,
            "title": "Discussion",
            "html_url": "...",
        }

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123/discussion_topics/10",
                "fetch_details": True,
            }
        )
        assert result["resource_type"] == "discussion_topic"
        assert result["recommended_tool"] == "get_discussion_entries"
        mock_client.get_discussion_topic_view.assert_called_once_with(
            course_id="123", topic_id="10"
        )

    def test_parses_page_url(self, mock_client):
        from tools import resolve_canvas_url

        mock_client.get_page.return_value = {
            "page_id": 1,
            "url": "home",
            "title": "Home",
            "html_url": "...",
        }

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123/pages/home",
                "fetch_details": True,
            }
        )
        assert result["resource_type"] == "page"
        assert result["recommended_tool"] == "canvas_get_page"
        assert mock_client.get_page.call_args.kwargs["url_or_id"] == "home"

    def test_course_only_url(self):
        from tools import resolve_canvas_url

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123",
                "fetch_details": False,
            }
        )
        assert result["resource_type"] == "course"
        assert result["recommended_tool"] == "get_course_overview"

    def test_parses_syllabus_url(self, mock_client):
        from tools import resolve_canvas_url

        mock_client.get_course.return_value = {
            "id": 123,
            "name": "Course",
            "course_code": "C",
            "term": {},
            "public_syllabus": False,
            "syllabus_body": "<p>S</p>",
            "html_url": "https://umd.instructure.com/courses/123",
        }

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123/assignments/syllabus",
                "fetch_details": True,
            }
        )
        assert result["resource_type"] == "syllabus"
        assert result["recommended_tool"] == "get_course_syllabus"
        assert mock_client.get_course.call_args.kwargs["course_id"] == "123"

    def test_parses_people_url(self, mock_client):
        from tools import resolve_canvas_url

        mock_client.list_course_users.return_value = []

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123/users",
                "fetch_details": True,
            }
        )
        assert result["resource_type"] == "course_people"
        assert result["recommended_tool"] == "list_course_people"
        assert mock_client.list_course_users.call_args.kwargs["course_id"] == "123"

    def test_parses_unknown_course_subpath(self):
        from tools import resolve_canvas_url

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/123/external_tools/9",
                "fetch_details": False,
            }
        )
        assert result["resource_type"] == "course_route"
        assert result["resource_id_raw"] == "external_tools"
        assert result["recommended_tool"] is None

    def test_keeps_course_id_unexpanded(self):
        from tools import resolve_canvas_url

        result = resolve_canvas_url(
            {
                "url": "https://umd.instructure.com/courses/1401744/home",
                "fetch_details": False,
            }
        )
        assert result["course_id"] == "1401744"


class TestCanvasGetPageTool:
    """Tests for canvas_get_page tool handler."""

    def test_rejects_non_page_url(self, mock_client):
        from tools import canvas_get_page

        result = canvas_get_page(
            {
                "course_id": "1",
                "url_or_id": "https://umd.instructure.com/courses/1/assignments/42",
            }
        )
        assert result.get("error") == "unsupported_url_pattern"
        assert result.get("suggested_tool") == "resolve_canvas_url"

    def test_accepts_page_url(self, mock_client):
        mock_client.get_page.return_value = {
            "page_id": 1,
            "url": "home",
            "title": "Home",
        }
        from tools import canvas_get_page

        result = canvas_get_page(
            {
                "course_id": "1",
                "url_or_id": "https://umd.instructure.com/courses/1/pages/home",
            }
        )
        assert result["page"]["title"] == "Home"
        assert mock_client.get_page.call_args.kwargs["url_or_id"] == "home"
        assert mock_client.get_page.call_args.kwargs["course_id"] == "1"


class TestDispatchToolCall:
    """Tests for dispatch_tool_call."""

    def test_unknown_tool(self):
        from specs.registry import dispatch_tool_call

        result = dispatch_tool_call("nonexistent_tool")
        assert result["error"] == "unknown_tool"
        assert "Unknown tool" in result["message"]
