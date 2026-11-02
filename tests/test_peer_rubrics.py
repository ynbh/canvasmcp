from __future__ import annotations

import pytest

from client.assignments import _peer_rubrics_from_html


def test_extracts_peer_criterion_feedback_and_skips_instructor_assessment():
    page = '''<script>window.ENV={"rubricAssessments":[
      {"rubric_assessment":{"assessment_type":"teacher","data":[]}},
      {"rubric_assessment":{"assessment_type":"peer_review",
        "assessor":{"user":{"name":"Alex Reviewer"}},
        "data":[{"criterion_id":"c1","comments":"Explain the example",
                 "points":4,"description":"Good"}]}}
    ]};</script>'''

    result = _peer_rubrics_from_html(
        page, rubric=[{"id": "c1", "description": "Audience analysis"}], anonymous=False
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
    page = '''"rubricAssessments":[{"rubric_assessment":{
      "assessment_type":"peer_review","assessor":{"user":{"name":"Private Name"}},
      "data":[]}}]'''

    result = _peer_rubrics_from_html(page, rubric=[], anonymous=True)

    assert result == [{"reviewer": "Reviewer 1", "criteria": []}]
    assert "Private Name" not in str(result)


def test_missing_assessment_payload_is_reported():
    with pytest.raises(ValueError, match="did not contain rubric assessments"):
        _peer_rubrics_from_html("<html>No reviews yet</html>", rubric=[], anonymous=False)
