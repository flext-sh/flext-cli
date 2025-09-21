"""CLI Session Service - Single responsibility for session management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from flext_cli.models import FlextCliModels
from flext_core import FlextDomainService, FlextLogger, FlextResult, FlextTypes


class FlextCliSessionService(FlextDomainService[FlextTypes.Core.Dict]):
    """Unified session service using single responsibility principle.

    Handles ALL session management operations for CLI ecosystem.
    ARCHITECTURAL COMPLIANCE: One class per module, nested helpers pattern.
    """

    def __init__(self) -> None:
        """Initialize session service with flext-core integration."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._sessions: dict[str, FlextCliModels.CliSession] = {}
        self._session_tracking_enabled = True

    class _SessionValidationHelper:
        """Nested helper for session validation - no loose functions."""

        @staticmethod
        def validate_session_id(session_id: object) -> FlextResult[str]:
            """Validate session ID parameter.

            Returns:
            FlextResult[str]: Description of return value.

            """
            if not isinstance(session_id, str) or not session_id.strip():
                return FlextResult[str].fail("Session ID must be a non-empty string")

            try:
                UUID(session_id)
                return FlextResult[str].ok(session_id.strip())
            except ValueError:
                return FlextResult[str].fail(f"Invalid session ID format: {session_id}")

        @staticmethod
        def validate_user_id(user_id: object) -> FlextResult[str | None]:
            """Validate user ID parameter.

            Returns:
            FlextResult[str | None]: Description of return value.

            """
            if user_id is None:
                return FlextResult[str | None].ok(None)

            if isinstance(user_id, str):
                return FlextResult[str | None].ok(user_id.strip() or None)

            return FlextResult[str | None].ok(str(user_id))

    class _SessionStateHelper:
        """Nested helper for session state management - no loose functions."""

        @staticmethod
        def create_session_metadata(user_id: str | None) -> FlextCliModels.CliSession:
            """Create session with proper metadata.

            Returns:
            FlextCliModels.CliSession: Description of return value.

            """
            session_id = str(uuid4())
            return FlextCliModels.CliSession(
                id=session_id,
                session_id=session_id,
                start_time=datetime.now(UTC),
                user_id=user_id,
            )

        @staticmethod
        def calculate_session_duration(session: FlextCliModels.CliSession) -> float:
            """Calculate session duration in seconds.

            Returns:
            float: Description of return value.

            """
            if session.end_time:
                return (session.end_time - session.start_time).total_seconds()

            return (datetime.now(UTC) - session.start_time).total_seconds()

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute session operation - FlextDomainService interface.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        self._logger.info("Executing session service operation")
        return FlextResult[FlextTypes.Core.Dict].ok({
            "active_sessions": len(self._sessions),
            "tracking_enabled": self._session_tracking_enabled,
        })

    def create_session(
        self, user_id: object = None
    ) -> FlextResult[FlextCliModels.CliSession]:
        """Create new CLI session with validation - single responsibility.

        Returns:
            FlextResult[FlextCliModels.CliSession]: Description of return value.

        """
        if not self._session_tracking_enabled:
            return FlextResult[FlextCliModels.CliSession].fail(
                "Session tracking is disabled"
            )

        # Validate user ID using nested helper
        user_validation = self._SessionValidationHelper.validate_user_id(user_id)
        if user_validation.is_failure:
            return FlextResult[FlextCliModels.CliSession].fail(
                user_validation.error or "User validation failed"
            )

        validated_user_id = user_validation.unwrap()

        try:
            # Create session using nested helper
            session = self._SessionStateHelper.create_session_metadata(
                validated_user_id
            )

            # Store session in tracking dictionary
            self._sessions[session.session_id] = session

            self._logger.info(f"Created session: {session.session_id}")
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session creation failed: {e}"
            )

    def end_session(self, session_id: object) -> FlextResult[FlextCliModels.CliSession]:
        """End CLI session with validation - single responsibility.

        Returns:
            FlextResult[FlextCliModels.CliSession]: Description of return value.

        """
        if not self._session_tracking_enabled:
            return FlextResult[FlextCliModels.CliSession].fail(
                "Session tracking is disabled"
            )

        # Validate session ID using nested helper
        validation_result = self._SessionValidationHelper.validate_session_id(
            session_id
        )
        if validation_result.is_failure:
            return FlextResult[FlextCliModels.CliSession].fail(
                validation_result.error or "Session ID validation failed"
            )

        validated_session_id = validation_result.unwrap()

        # Check if session exists
        if validated_session_id not in self._sessions:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session not found: {validated_session_id}"
            )

        try:
            # End session and calculate duration
            session = self._sessions[validated_session_id]
            session.end_time = datetime.now(UTC)

            # Remove from active sessions
            del self._sessions[validated_session_id]

            self._logger.info(f"Ended session: {validated_session_id}")
            return FlextResult[FlextCliModels.CliSession].ok(session)
        except Exception as e:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session end failed: {e}"
            )

    def get_session(self, session_id: object) -> FlextResult[FlextCliModels.CliSession]:
        """Get session information - single responsibility.

        Returns:
            FlextResult[FlextCliModels.CliSession]: Description of return value.

        """
        if not self._session_tracking_enabled:
            return FlextResult[FlextCliModels.CliSession].fail(
                "Session tracking is disabled"
            )

        # Validate session ID using nested helper
        validation_result = self._SessionValidationHelper.validate_session_id(
            session_id
        )
        if validation_result.is_failure:
            return FlextResult[FlextCliModels.CliSession].fail(
                validation_result.error or "Session validation failed"
            )

        validated_session_id = validation_result.unwrap()

        # Check if session exists
        if validated_session_id not in self._sessions:
            return FlextResult[FlextCliModels.CliSession].fail(
                f"Session not found: {validated_session_id}"
            )

        session = self._sessions[validated_session_id]
        return FlextResult[FlextCliModels.CliSession].ok(session)

    def list_active_sessions(self) -> FlextResult[list[FlextCliModels.CliSession]]:
        """List all active sessions - single responsibility.

        Returns:
            FlextResult[list[FlextCliModels.CliSession]]: Description of return value.

        """
        if not self._session_tracking_enabled:
            return FlextResult[list[FlextCliModels.CliSession]].fail(
                "Session tracking is disabled"
            )

        active_sessions = list(self._sessions.values())
        return FlextResult[list[FlextCliModels.CliSession]].ok(active_sessions)

    def get_session_statistics(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get session statistics - single responsibility.

        Returns:
            FlextResult[FlextTypes.Core.Dict]: Description of return value.

        """
        if not self._session_tracking_enabled:
            return FlextResult[FlextTypes.Core.Dict].fail(
                "Session tracking is disabled"
            )

        try:
            total_sessions = len(self._sessions)
            session_durations = [
                self._SessionStateHelper.calculate_session_duration(session)
                for session in self._sessions.values()
            ]

            statistics = {
                "total_active_sessions": total_sessions,
                "average_duration_seconds": sum(session_durations)
                / len(session_durations)
                if session_durations
                else 0,
                "longest_session_seconds": max(session_durations)
                if session_durations
                else 0,
                "shortest_session_seconds": min(session_durations)
                if session_durations
                else 0,
                "sessions_by_user": self._get_sessions_by_user(),
            }

            return FlextResult[FlextTypes.Core.Dict].ok(dict(statistics))
        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Statistics calculation failed: {e}"
            )

    def _get_sessions_by_user(self) -> dict[str, int]:
        """Get session count by user - internal helper.

        Returns:
            dict[str, int]: Description of return value.

        """
        user_counts: dict[str, int] = {}

        for session in self._sessions.values():
            user_key = session.user_id or "anonymous"
            user_counts[user_key] = user_counts.get(user_key, 0) + 1

        return user_counts

    def configure_session_tracking(self, *, enabled: bool) -> FlextResult[None]:
        """Configure session tracking - single responsibility.

        Returns:
            FlextResult[None]: Description of return value.

        """
        try:
            self._session_tracking_enabled = bool(enabled)

            if not enabled:
                # Clear all sessions when disabling tracking
                self._sessions.clear()
                self._logger.info("Session tracking disabled, all sessions cleared")
            else:
                self._logger.info("Session tracking enabled")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration failed: {e}")

    def clear_all_sessions(self) -> FlextResult[int]:
        """Clear all active sessions - single responsibility.

        Returns:
            FlextResult[int]: Description of return value.

        """
        if not self._session_tracking_enabled:
            return FlextResult[int].fail("Session tracking is disabled")

        try:
            session_count = len(self._sessions)
            self._sessions.clear()

            self._logger.info(f"Cleared {session_count} sessions")
            return FlextResult[int].ok(session_count)
        except Exception as e:
            return FlextResult[int].fail(f"Session clearing failed: {e}")


__all__ = ["FlextCliSessionService"]
