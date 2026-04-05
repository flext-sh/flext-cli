"""FLEXT CLI enums and enum-backed settings constants."""

from __future__ import annotations

from enum import StrEnum, unique


class FlextCliConstantsEnums:
    """CLI enums grouped for composition by the public constants facade."""

    @unique
    class OutputFormats(StrEnum):
        """Output format enum for CLI commands."""

        JSON = "json"
        YAML = "yaml"
        CSV = "csv"
        TABLE = "table"
        PLAIN = "plain"

    @unique
    class CommandStatus(StrEnum):
        """Command execution status enum."""

        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"

    @unique
    class MessageTypes(StrEnum):
        """Message types enum."""

        INFO = "info"
        ERROR = "error"
        WARNING = "warning"
        SUCCESS = "success"
        DEBUG = "debug"

    @unique
    class LogVerbosity(StrEnum):
        """Log verbosity enum."""

        COMPACT = "compact"
        DETAILED = "detailed"
        FULL = "full"

    @unique
    class ServiceStatus(StrEnum):
        """Service status enum."""

        OPERATIONAL = "operational"

    class Settings:
        """Settings constants."""

        @unique
        class LogLevel(StrEnum):
            """Log level enum."""

            DEBUG = "DEBUG"
            INFO = "INFO"
            WARNING = "WARNING"
            ERROR = "ERROR"
            CRITICAL = "CRITICAL"
