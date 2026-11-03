from __future__ import annotations

import pytest

from client.assignments import _rubric_assessments_from_html
from tools.assignments import _peer_rubric_feedback


def test_extracts_embedded_rubric_assessments():
    page = '''<script>window.ENV={"rubricAssessments":[
      {"rubric_assessment":{"assessment_type":"grading","data":[]}},
      {"rubric_assessment":{"assessment_type":"peer_review","data":[]}}
    ]};</script>'''

    assert [a["assessment_type"] for a in _rubric_assessments_from_html(page)] == [
        "grading",
        "peer_review",
    ]


def test_missing_assessment_payload_is_reported():
    with pytest.raises(ValueError, match="did not contain rubric assessments"):
        _rubric_assessments_from_html("<html>No reviews yet</html>")


def test_peer_feedback_keeps_peer_criteria_and_skips_instructor_assessment():
    assessments = [
        {"assessment_type": "grading", "data": []},
        {
            "assessment_type": "peer_review",
            "assessor": {"user": {"name": "Alex Reviewer"}},
            "data": [
                {"criterion_id": "c1", "comments": "Explain the example", "points": 4, "description": "Good"}
            ],
        },
    ]

    result = _peer_rubric_feedback(
        assessments, rubric=[{"id": "c1", "description": "Audience analysis"}], anonymous=False
    )

    assert result == [
        {
            "reviewer": "Alex Reviewer",
            "criteria": [
                {
                    "criterion_id": "c1",
                    "description": "Audience analysis",
                    "comments": "Explain the example",
                    "points": 4,
                    "rating": "Good",
                }
            ],
        }
    ]


def test_anonymous_peer_review_does_not_expose_assessor_name():
    assessments = [
        {"assessment_type": "peer_review", "assessor": {"user": {"name": "Private Name"}}, "data": []}
    ]

    result = _peer_rubric_feedback(assessments, rubric=[], anonymous=True)

    assert result == [{"reviewer": "Reviewer 1", "criteria": []}]
    assert "Private Name" not in str(result)
