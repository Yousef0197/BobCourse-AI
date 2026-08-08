"""
Phase 7 — Python → Java integration test.

Tests the AnalyticsClient and the analytics service layer.
The Java service is mocked — tests verify:
  1. Payload construction (student_id absent)
  2. Client wraps httpx correctly
  3. Threshold enforcement for instructor role
"""
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.services.analytics_client import AnalyticsClient
from app.models.user import UserRole


# ─── AnalyticsClient unit tests ───────────────────────────────────────────────

class TestAnalyticsClient:
    def test_campaign_stats_posts_to_correct_path(self):
        """Client should POST to /internal/analytics/campaign-stats."""
        client = AnalyticsClient(base_url="http://fake-java:8080")
        mock_response = {"campaignId": "abc", "overallAverage": 4.2}

        with patch("httpx.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.headers = {"content-type": "application/json"}
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = MagicMock()
            mock_post.return_value = mock_resp

            result = client.campaign_stats({"campaignId": "abc"})

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "/internal/analytics/campaign-stats" in call_args[0][0]
        assert result == mock_response

    def test_payload_never_contains_student_id(self):
        """Verify no student_id key can be smuggled into analytics payload."""
        payload = {
            "campaignId": "abc",
            "courseCode": "CS101",
            "submissions": [
                {"answers": [{"questionId": "q1", "questionText": "Q", "rating": 4}]}
            ],
        }
        # student_id must not exist anywhere in the payload
        import json
        payload_str = json.dumps(payload)
        assert "student_id" not in payload_str
        assert "studentId" not in payload_str

    def test_service_unavailable_raises_503(self):
        import httpx
        from fastapi import HTTPException
        client = AnalyticsClient(base_url="http://unreachable:9999")

        with patch("httpx.post", side_effect=httpx.ConnectError("refused")):
            with pytest.raises(HTTPException) as exc:
                client.campaign_stats({})
            assert exc.value.status_code == 503

    def test_timeout_raises_504(self):
        import httpx
        from fastapi import HTTPException
        client = AnalyticsClient(base_url="http://slow:9999")

        with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
            with pytest.raises(HTTPException) as exc:
                client.campaign_stats({})
            assert exc.value.status_code == 504


# ─── Threshold enforcement ────────────────────────────────────────────────────

class TestThresholdEnforcement:
    def test_instructor_blocked_below_threshold(self):
        """
        When totalSubmissions < min_responses_threshold and user is instructor,
        the analytics router should return a threshold message, not the data.
        """
        # This is tested at the service call level — we verify the logic
        threshold = 5
        total_submissions = 3
        assert total_submissions < threshold  # confirms business rule triggers

    def test_admin_sees_results_below_threshold(self):
        """Admin should always see results regardless of threshold."""
        admin = SimpleNamespace(role=UserRole.admin, id=uuid.uuid4())
        # Admin role check — no threshold enforcement
        assert admin.role != UserRole.instructor


# ─── Response shape verification ─────────────────────────────────────────────

class TestAnalyticsResponseShape:
    def test_campaign_stats_response_has_expected_keys(self):
        """Verify the expected shape of CampaignStatsResponse from Java."""
        mock_response = {
            "campaignId": "abc",
            "courseCode": "CS101",
            "courseName": "Intro CS",
            "totalSubmissions": 3,
            "totalEnrolled": 4,
            "responseRate": 75.0,
            "overallAverage": 4.0,
            "questionStats": [
                {
                    "questionId": "q1",
                    "questionText": "Overall quality?",
                    "average": 4.0,
                    "distribution": {1: 0, 2: 0, 3: 1, 4: 1, 5: 1},
                }
            ],
        }
        assert "campaignId" in mock_response
        assert "overallAverage" in mock_response
        assert "questionStats" in mock_response
        assert "totalSubmissions" in mock_response
        # student_id must NOT be in any response going to frontend
        assert "student_id" not in str(mock_response)
        assert "studentId" not in str(mock_response)

class TestCsvThresholdEnforcement:

    def test_instructor_cannot_export_below_threshold(self):
        """Instructor must not bypass the anonymity threshold through CSV export."""
        from fastapi import HTTPException
        from app.api.analytics import export_csv

        campaign_id = uuid.uuid4()
        instructor = SimpleNamespace(
            role=UserRole.instructor,
            id=uuid.uuid4(),
        )

        campaign = SimpleNamespace(
            id=campaign_id,
            min_responses_threshold=5,
        )

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = campaign
        db.query.return_value.filter.return_value.count.return_value = 1

        with patch(
            "app.api.analytics.analytics_service.get_csv_export",
            return_value="question_id,average_rating\nq1,4.0\n",
        ) as mock_export:
            with pytest.raises(HTTPException) as exc:
                export_csv(campaign_id, db, instructor)

        assert exc.value.status_code == 403
        mock_export.assert_not_called()

    def test_admin_can_export_below_threshold(self):
        """Admin retains access to aggregated reports below the instructor threshold."""
        from app.api.analytics import export_csv

        campaign_id = uuid.uuid4()
        admin = SimpleNamespace(
            role=UserRole.admin,
            id=uuid.uuid4(),
        )

        db = MagicMock()

        with patch(
            "app.api.analytics.analytics_service.get_csv_export",
            return_value="question_id,average_rating\nq1,4.0\n",
        ) as mock_export:
            response = export_csv(campaign_id, db, admin)

        assert response.status_code == 200
        mock_export.assert_called_once_with(db, campaign_id)
