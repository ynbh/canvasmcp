from __future__ import annotations

from unittest import mock


class TestGetToday:
    """Tests for get_today tool handler."""

    def test_returns_iso_date(self):
        from tools import get_today

        result = get_today({})
        assert "today" in result
        assert len(result["today"]) == 10


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
        assert result["count"] == 1
        assert result["courses"][0]["name"] == "Math 101"

    def test_empty_courses(self, mock_client):
        mock_client.list_courses.return_value = []
        from tools import list_courses

        result = list_courses({})
        assert result["count"] == 0


class TestResolveCourseTool:
    """Tests for resolve_course tool handler."""

    def test_empty_query_returns_no_matches(self, mock_client):
        from tools import resolve_course

        result = resolve_course({"query": ""})
        assert result["count"] == 0

    def test_scores_and_sorts(self, mock_client):
        mock_client.list_courses.return_value = [
            {
                "id": 1,
                "name": "CMSC430",
                "course_code": "CMSC430",
                "workflow_state": "active",
            },
            {
                "id": 2,
                "name": "ENGL101",
                "course_code": "ENGL101",
                "workflow_state": "active",
            },
        ]
        from tools import resolve_course

        result = resolve_course({"query": "CMSC430"})
        assert result["count"] >= 1
        assert result["matches"][0]["name"] == "CMSC430"


class TestListCourseAssignmentsTool:
    """Tests for list_course_assignments tool handler."""

    def test_requires_course_id(self, mock_client):
        from tools import list_course_assignments

        result = list_course_assignments({})
        assert "error" in result

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
        assert result["count"] == 1
        assert result["assignments"][0]["name"] == "HW1"


class TestGetAssignmentDetailsTool:
    """Tests for get_assignment_details tool handler."""

    def test_requires_both_ids(self, mock_client):
        from tools import get_assignment_details

        assert "error" in get_assignment_details({"course_id": "1"})
        assert "error" in get_assignment_details({"assignment_id": "1"})

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
        assert result["assignment"]["name"] == "Midterm"
        assert result["assignment"]["rubric"][0]["description"] == "Correctness"


class TestGetAssignmentRubricTool:
    """Tests for get_assignment_rubric tool handler."""

    def test_requires_both_ids(self, mock_client):
        from tools import get_assignment_rubric

        assert "error" in get_assignment_rubric({"course_id": "1"})
        assert "error" in get_assignment_rubric({"assignment_id": "1"})

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
        assert result["assessment_source"] == "submission"
        mock_client.list_submissions.assert_not_called()

    def test_falls_back_to_submission_include_for_assessment(self, mock_client):
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
        mock_client.list_submissions.assert_called_once_with(
            course_id="1",
            student_id="self",
            assignment_ids=["42"],
            include=["rubric_assessment"],
            grouped=False,
            limit=1,
        )


class TestListCourseFilesTool:
    """Tests for list_course_files tool handler."""

    def test_requires_course_id(self, mock_client):
        from tools import list_course_files

        assert "error" in list_course_files({})

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
        assert result["count"] == 1
        assert result["files"][0]["display_name"] == "notes.pdf"


class TestListCoursePagesTool:
    """Tests for list_course_pages tool handler."""

    def test_requires_course_id(self, mock_client):
        from tools import list_course_pages

        assert "error" in list_course_pages({})

    def test_returns_pages(self, mock_client):
        mock_client.list_pages.return_value = [
            {"page_id": 1, "url": "home", "title": "Home Page", "published": True},
        ]
        from tools import list_course_pages

        result = list_course_pages({"course_id": "123"})
        assert result["count"] == 1
        assert result["pages"][0]["title"] == "Home Page"


class TestListCourseTabsTool:
    """Tests for list_course_tabs tool handler."""

    def test_requires_course_id(self, mock_client):
        from tools import list_course_tabs

        assert "error" in list_course_tabs({})

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
        assert result["count"] == 2
        assert result["tabs"][0]["id"] == "home"
        assert result["tabs"][1]["label"] == "Syllabus"


class TestGetCourseTabTool:
    """Tests for get_course_tab tool handler."""

    def test_requires_both_params(self, mock_client):
        from tools import get_course_tab

        assert "error" in get_course_tab({"course_id": "1"})
        assert "error" in get_course_tab({"tab_id": "home"})

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

    def test_requires_course_id(self, mock_client):
        from tools import list_discussion_topics

        assert "error" in list_discussion_topics({})

    def test_returns_topics(self, mock_client):
        mock_client.list_discussion_topics.return_value = [
            {"id": 10, "title": "Week 1 Discussion", "assignment_id": 42},
        ]
        mock_client.list_assignments.return_value = []
        from tools import list_discussion_topics

        result = list_discussion_topics({"course_id": "123"})
        assert result["count"] == 1
        assert result["topics"][0]["title"] == "Week 1 Discussion"

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

    def test_requires_course_ids(self, mock_client):
        from tools import list_announcements

        assert "error" in list_announcements({})

    def test_returns_announcements(self, mock_client):
        mock_client.list_announcements.return_value = [
            {"id": 5, "title": "Welcome!", "message": "<p>Hi</p>"},
        ]
        from tools import list_announcements

        result = list_announcements({"course_ids": ["123"]})
        assert result["count"] == 1


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
        assert result["count"] == 1
        assert result["todo"][0]["assignment"]["name"] == "Midterm"


class TestListCoursePeopleTool:
    """Tests for list_course_people tool handler."""

    def test_requires_course_id(self, mock_client):
        from tools import list_course_people

        assert "error" in list_course_people({})

    def test_returns_people(self, mock_client):
        mock_client.list_course_users.return_value = [
            {"id": 1, "name": "Jane Doe", "email": "jane@umd.edu", "enrollments": []},
        ]
        from tools import list_course_people

        result = list_course_people({"course_id": "123"})
        assert result["count"] == 1
        assert result["people"][0]["name"] == "Jane Doe"


class TestResolveCanvasUrlTool:
    """Tests for resolve_canvas_url tool handler."""

    def test_requires_url(self):
        from tools import resolve_canvas_url

        assert "error" in resolve_canvas_url({})

    def test_parses_assignment_url(self):
        from tools import resolve_canvas_url

        with mock.patch("tools.misc.canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
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

    def test_parses_discussion_url(self):
        from tools import resolve_canvas_url

        with mock.patch("tools.misc.canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
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

    def test_parses_page_url(self):
        from tools import resolve_canvas_url

        with mock.patch("tools.misc.canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
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

    def test_course_only_url(self):
        from tools import resolve_canvas_url

        with mock.patch("tools.misc.canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            from auth import CanvasAPIError

            mock_client.get_course.side_effect = CanvasAPIError("not found")

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123",
                    "fetch_details": False,
                }
            )
            assert result["resource_type"] == "course"
            assert result["recommended_tool"] == "get_course_overview"

    def test_parses_syllabus_url(self):
        from tools import resolve_canvas_url

        with mock.patch("tools.misc.canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
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

    def test_parses_people_url(self):
        from tools import resolve_canvas_url

        with mock.patch("tools.misc.canvas_client") as mock_client_fn:
            mock_client = mock.MagicMock()
            mock_client_fn.return_value = mock_client
            mock_client.list_course_users.return_value = []

            result = resolve_canvas_url(
                {
                    "url": "https://umd.instructure.com/courses/123/users",
                    "fetch_details": True,
                }
            )
            assert result["resource_type"] == "course_people"
            assert result["recommended_tool"] == "list_course_people"

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

    def test_requires_both_params(self, mock_client):
        from tools import canvas_get_page

        assert "error" in canvas_get_page({"course_id": "1"})
        assert "error" in canvas_get_page({"url_or_id": "home"})

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
        assert "page" in result
        assert result["page"]["title"] == "Home"


class TestDispatchToolCall:
    """Tests for dispatch_tool_call."""

    def test_unknown_tool(self):
        from specs.registry import dispatch_tool_call

        result = dispatch_tool_call("nonexistent_tool")
        assert "error" in result
        assert "Unknown tool" in result["error"]

    def test_dispatches_get_today(self):
        from specs.registry import dispatch_tool_call

        result = dispatch_tool_call("get_today")
        assert "today" in result
