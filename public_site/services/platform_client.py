"""
Platform API Client for Public Site Enhanced Features

Provides optional integration with main platform via API calls.
Falls back gracefully when main platform is unavailable.
"""

import base64
import json
import logging
import uuid
from typing import Any

import requests
from cryptography.fernet import Fernet
from django.conf import settings

logger = logging.getLogger(__name__)


class PlatformAPIClient:
    """Client for optional integration with main garden platform."""

    def __init__(self):
        self.base_url = getattr(
            settings, "MAIN_PLATFORM_API_URL", "http://garden-platform:8000"
        )
        self.timeout = getattr(settings, "AI_API_TIMEOUT", 30)
        self.quick_timeout = getattr(settings, "AI_QUICK_ANALYSIS_TIMEOUT", 10)

        # Secure API configuration
        self.api_key = getattr(settings, "BACKEND_API_KEY", None)
        self.encryption_key = getattr(settings, "FORM_ENCRYPTION_KEY", None)
        self._cipher = None

        if self.encryption_key:
            try:
                # Ensure key is properly formatted for Fernet
                if isinstance(self.encryption_key, str):
                    key_bytes = self.encryption_key.encode()
                    if (
                        len(key_bytes) != 44
                    ):  # Fernet key should be 44 bytes when base64 encoded
                        key_bytes = base64.urlsafe_b64encode(key_bytes[:32])
                    self._cipher = Fernet(key_bytes)
                else:
                    self._cipher = Fernet(self.encryption_key)
            except Exception as e:
                logger.warning(f"Failed to initialize encryption: {e}")
                self._cipher = None

    def _encrypt_data(self, data: dict[str, Any]) -> str | None:
        """Encrypt data payload using Fernet encryption."""
        if not self._cipher:
            return None
        try:
            json_data = json.dumps(data, default=str)
            encrypted_data = self._cipher.encrypt(json_data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None

    def _make_request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        timeout: int | None = None,
        method: str = "POST",
        use_secure_api: bool = False,
    ) -> dict[str, Any] | None:
        """Make API request with graceful error handling."""
        try:
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            timeout = timeout or self.timeout
            headers = {"Content-Type": "application/json"}

            # Add API key authentication for secure endpoints
            if use_secure_api and self.api_key:
                headers["X-API-Key"] = self.api_key

            if method.upper() == "POST":
                response = requests.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=timeout,
                )
            else:
                response = requests.get(
                    url, params=data, headers=headers, timeout=timeout
                )

            if response.status_code == 200:
                return response.json()
            logger.warning(
                f"Platform API returned {response.status_code} for {endpoint}"
            )
            return None

        except requests.exceptions.Timeout:
            logger.warning(f"Platform API timeout for {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            logger.debug(f"Platform API unavailable for {endpoint}")
            return None
        except Exception:
            logger.exception("Platform API error for {endpoint}")
            return None

    def analyze_content(
        self, content: str, analysis_type: str = "comprehensive"
    ) -> dict[str, Any] | None:
        """
        Optional AI content analysis.

        Returns:
            Dict with analysis results if successful, None if unavailable
        """
        data = {
            "content": content,
            "analysis_type": analysis_type,
            "options": {
                "include_charts": True,
                "include_suggestions": True,
                "min_confidence": getattr(settings, "AI_MIN_CONFIDENCE", 0.7),
            },
        }

        result = self._make_request("/api/v1/ai/analyze-content/", data, self.timeout)
        if result:
            logger.info(f"AI analysis completed for content ({len(content)} chars)")

        return result

    def quick_analyze_content(self, content: str) -> dict[str, Any] | None:
        """Quick content analysis with shorter timeout."""
        data = {
            "content": content,
            "analysis_type": "quick",
            "options": {
                "include_charts": False,
                "include_suggestions": True,
                "min_confidence": 0.6,
            },
        }

        return self._make_request(
            "/api/v1/ai/analyze-content/", data, self.quick_timeout
        )

    def notify_contact_submission(self, contact_data: dict[str, Any]) -> bool:
        """
        Notify main platform of contact form submission for enhanced processing.

        Returns:
            True if notification sent successfully, False otherwise
        """
        result = self._make_request(
            "/api/v1/contact-notifications/", contact_data, self.quick_timeout
        )

        if result:
            logger.info(
                f"Contact notification sent for {contact_data.get('email', 'unknown')}"
            )
            return True

        return False

    def create_enhanced_contact(
        self, form_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Create contact with full CRM integration via API.

        Returns:
            Contact data if successful, None if unavailable
        """
        result = self._make_request("/api/v1/contacts/", form_data, self.timeout)

        if result:
            logger.info(
                f"Enhanced contact created via API for {form_data.get('email', 'unknown')}"
            )

        return result

    def get_portfolio_summary(
        self, strategy: str | None = None
    ) -> dict[str, Any] | None:
        """
        Get portfolio summary data for public display.

        Args:
            strategy: Optional strategy filter

        Returns:
            Portfolio summary if available, None otherwise
        """
        params = {"strategy": strategy} if strategy else {}
        result = self._make_request(
            "/api/v1/portfolio/public-summary/", params, self.quick_timeout, "GET"
        )

        if result:
            logger.info(
                f"Portfolio summary retrieved for strategy: {strategy or 'all'}"
            )

        return result

    def get_research_insights(
        self, topic: str | None = None, limit: int = 5
    ) -> dict[str, Any] | None:
        """
        Get recent research insights for public display.

        Args:
            topic: Optional topic filter
            limit: Number of insights to return

        Returns:
            Research insights if available, None otherwise
        """
        params = {"topic": topic, "limit": limit}
        result = self._make_request(
            "/api/v1/research/public-insights/", params, self.quick_timeout, "GET"
        )

        if result:
            logger.info(f"Research insights retrieved for topic: {topic or 'all'}")

        return result

    def secure_contact_submission(
        self, form_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Submit contact form data using secure encrypted API.

        Args:
            form_data: Contact form data to submit

        Returns:
            Submission result with confirmation details if successful
        """
        if not self.api_key:
            logger.warning("No API key configured for secure contact submission")
            return None

        # Add submission metadata
        submission_data = {
            "submission_id": str(uuid.uuid4()),
            "form_type": "contact",
            "submitted_at": str(uuid.uuid1().time),
            "data": form_data,
        }

        # Encrypt the payload if encryption is available
        if self._cipher:
            encrypted_payload = self._encrypt_data(submission_data)
            if encrypted_payload:
                payload = {"encrypted_data": encrypted_payload}
            else:
                logger.warning(
                    "Encryption failed, falling back to unencrypted submission"
                )
                payload = submission_data
        else:
            logger.info("No encryption key configured, sending unencrypted data")
            payload = submission_data

        result = self._make_request(
            "/api/v1/secure/contact-submission/",
            payload,
            self.timeout,
            use_secure_api=True,
        )

        if result:
            logger.info(
                f"Secure contact submission successful: {result.get('submission_id', 'unknown')}"
            )

        return result

    def secure_onboarding_submission(
        self, form_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Submit onboarding form data using secure encrypted API.

        Args:
            form_data: Onboarding form data to submit

        Returns:
            Submission result with confirmation details if successful
        """
        if not self.api_key:
            logger.warning("No API key configured for secure onboarding submission")
            return None

        # Add submission metadata
        submission_data = {
            "submission_id": str(uuid.uuid4()),
            "form_type": "onboarding",
            "submitted_at": str(uuid.uuid1().time),
            "data": form_data,
        }

        # Encrypt the payload if encryption is available
        if self._cipher:
            encrypted_payload = self._encrypt_data(submission_data)
            if encrypted_payload:
                payload = {"encrypted_data": encrypted_payload}
            else:
                logger.warning(
                    "Encryption failed, falling back to unencrypted submission"
                )
                payload = submission_data
        else:
            logger.info("No encryption key configured, sending unencrypted data")
            payload = submission_data

        result = self._make_request(
            "/api/v1/secure/onboarding-submission/",
            payload,
            self.timeout,
            use_secure_api=True,
        )

        if result:
            logger.info(
                f"Secure onboarding submission successful: {result.get('submission_id', 'unknown')}"
            )

        return result

    def check_submission_status(self, submission_id: str) -> dict[str, Any] | None:
        """
        Check the status of a form submission.

        Args:
            submission_id: ID of the submission to check

        Returns:
            Status information if available
        """
        if not self.api_key or not submission_id:
            return None

        return self._make_request(
            f"/api/v1/secure/submission-status/{submission_id}/",
            timeout=self.quick_timeout,
            method="GET",
            use_secure_api=True,
        )

    def health_check(self) -> bool:
        """
        Check if main platform is available.

        Returns:
            True if platform is healthy, False otherwise
        """
        result = self._make_request("/api/v1/health/", timeout=5, method="GET")
        return result is not None


# Global client instance
platform_client = PlatformAPIClient()
