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
        XML = "xml"

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
    class PipelineStageStatus(StrEnum):
        """Pipeline stage execution status enum."""

        OK = "ok"
        SKIPPED = "skipped"
        FAILED = "failed"

    @unique
    class TypeKind(StrEnum):
        """Typed extraction kind enum."""

        STR = "str"
        BOOL = "bool"
        DICT = "dict"

    @unique
    class ServiceStatus(StrEnum):
        """Service status enum."""

        OPERATIONAL = "operational"

    @unique
    class TabularFormat(StrEnum):
        """Tabulate library format string authority — for table rendering."""

        PLAIN = "plain"
        SIMPLE = "simple"
        GRID = "grid"
        FANCY_GRID = "fancy_grid"
        PIPE = "pipe"
        ORGTBL = "orgtbl"
        RST = "rst"
        MEDIAWIKI = "mediawiki"
        HTML = "html"
        LATEX = "latex"
        PSQL = "psql"
        PRETTY = "pretty"
        TABLE = "table"

    @unique
    class MessageStyles(StrEnum):
        """Rich style string authority — single source of truth for all style values."""

        BLUE = "blue"
        GREEN = "green"
        RED = "red"
        YELLOW = "yellow"
        CYAN = "cyan"
        WHITE = "white"
        DIM = "dim"
        BOLD = "bold"
        BOLD_BLUE = "bold blue"
        BOLD_GREEN = "bold green"
        BOLD_RED = "bold red"
        BOLD_YELLOW = "bold yellow"
        BOLD_CYAN = "bold cyan"
        BOLD_WHITE = "bold white"
        BOLD_MAGENTA = "bold magenta"
        BOLD_WHITE_ON_BLUE = "bold white on blue"


__all__ = [
    "FlextCliConstantsEnums",
]
