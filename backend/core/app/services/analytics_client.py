"""
Analytics HTTP client — calls Java analytics service from Python.
student_id is stripped before any payload is sent to Java.
"""
import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class AnalyticsClient:
    """Thin httpx wrapper around the Java analytics service."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        self._base = (base_url or settings.ANALYTICS_SERVICE_URL).rstrip("/")
        self._timeout = timeout

    def _post(self, path: str, payload: dict) -> dict | str:
        url = f"{self._base}{path}"
        try:
            resp = httpx.post(url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if "text/plain" in content_type:
                return resp.text
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Analytics service is unavailable",
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Analytics service timed out",
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Analytics service error: {e.response.status_code}",
            )

    def campaign_stats(self, payload: dict) -> dict:
        return self._post("/internal/analytics/campaign-stats", payload)

    def course_trends(self, payload: dict) -> dict:
        return self._post("/internal/analytics/course-trends", payload)

    def dashboard(self, payload: dict) -> dict:
        return self._post("/internal/analytics/dashboard", payload)

    def export_csv(self, payload: dict) -> str:
        return self._post("/internal/analytics/export-csv", payload)


# Module-level singleton
analytics_client = AnalyticsClient()
