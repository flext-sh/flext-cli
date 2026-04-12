"""FLEXT CLI example constants."""

from __future__ import annotations

import re
from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from flext_cli import c


class ExamplesFlextCliConstants(c):
    """Public examples constants facade extending flext-cli constants."""

    EXAMPLE_DEPLOYMENT_ENVIRONMENTS: Final[tuple[str, ...]] = (
        "development",
        "staging",
        "production",
    )
    EXAMPLE_DEPLOYMENT_ENVIRONMENTS_SET: Final[frozenset[str]] = frozenset(
        EXAMPLE_DEPLOYMENT_ENVIRONMENTS,
    )
    EXAMPLE_DEPLOYMENT_ENVIRONMENTS_SHORT: Final[tuple[str, ...]] = (
        "dev",
        "staging",
        "prod",
    )
    EXAMPLE_REQUIRED_DATA_FIELDS: Final[tuple[str, ...]] = ("id", "name", "value")
    EXAMPLE_DATABASE_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
        "host",
        "name",
        "username",
        "password",
    )
    EXAMPLE_DEFAULT_SHELL_ITEMS: Final[tuple[str, ...]] = (
        "item1",
        "item2",
        "item3",
        "test_item",
    )
    EXAMPLE_SAMPLE_FILES: Final[tuple[str, ...]] = (
        "file1",
        "file2",
        "file3",
        "file4",
    )
    EXAMPLE_TABLE_HEADERS_FIELD_VALUE: Final[tuple[str, str]] = ("Field", "Value")
    EXAMPLE_TABLE_HEADERS_SETTING_VALUE: Final[tuple[str, str]] = (
        "Setting",
        "Value",
    )

    EXAMPLE_REGEX_EMAIL: Final[re.Pattern[str]] = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    EXAMPLE_REGEX_DOT: Final[re.Pattern[str]] = re.compile(r"\.")

    EXAMPLE_DEFAULT_HOST: Final[str] = "localhost"
    EXAMPLE_DEFAULT_DB_PORT: Final[int] = 5432
    EXAMPLE_DEFAULT_APP_PORT: Final[int] = 8080
    EXAMPLE_DEFAULT_MAX_WORKERS: Final[int] = 4
    EXAMPLE_DEFAULT_TIMEOUT_SECONDS: Final[int] = 30
    EXAMPLE_DEFAULT_CPU_LIMIT: Final[float] = 1.0
    EXAMPLE_DEFAULT_CPU_LIMIT_PROMPTS: Final[float] = 2.5
    EXAMPLE_DEFAULT_PERCENTAGE: Final[int] = 50
    EXAMPLE_DEFAULT_CONNECTION_POOL: Final[int] = 10

    EXAMPLE_MIN_PORT: Final[int] = 1024
    EXAMPLE_MAX_PORT: Final[int] = 65535
    EXAMPLE_MAX_WORKERS: Final[int] = 32
    EXAMPLE_MAX_CONNECTION_POOL: Final[int] = 100
    EXAMPLE_MIN_PASSWORD_LENGTH: Final[int] = 8

    EXAMPLE_DEFAULT_APP_NAME: Final[str] = "my-app"
    EXAMPLE_DEFAULT_TOOL_NAME: Final[str] = "my-cli-tool"
    EXAMPLE_DEFAULT_ENVIRONMENT: Final[str] = "development"
    EXAMPLE_DEFAULT_APP_VERSION: Final[str] = "1.0.0"
    EXAMPLE_DEFAULT_LOG_LEVEL: Final[str] = "INFO"
    EXAMPLE_DEFAULT_DB_URL: Final[str] = "postgresql://localhost:5432/myapp"
    EXAMPLE_DEFAULT_REDIS_URL: Final[str] = "redis://localhost:6379"
    EXAMPLE_DEFAULT_TEMP_SUBDIR: Final[str] = "myapp"

    EXAMPLE_ENV_KEY_APP_NAME: Final[str] = "APP_NAME"
    EXAMPLE_ENV_KEY_API_KEY: Final[str] = "API_KEY"
    EXAMPLE_ENV_KEY_MAX_WORKERS: Final[str] = "MAX_WORKERS"
    EXAMPLE_ENV_KEY_TIMEOUT: Final[str] = "TIMEOUT"
    EXAMPLE_ENV_KEY_DATABASE_URL: Final[str] = "DATABASE_URL"
    EXAMPLE_ENV_KEY_REDIS_URL: Final[str] = "REDIS_URL"
    EXAMPLE_ENV_KEY_ENABLE_METRICS: Final[str] = "ENABLE_METRICS"
    EXAMPLE_ENV_KEY_LOG_LEVEL: Final[str] = "LOG_LEVEL"
    EXAMPLE_ENV_KEY_TEMP_DIR: Final[str] = "TEMP_DIR"
    EXAMPLE_ENV_KEY_ENVIRONMENT: Final[str] = "ENVIRONMENT"
    EXAMPLE_ENV_VALUE_PRODUCTION: Final[str] = "production"

    EXAMPLE_ENV_MAP_MY_APP: Final[Mapping[str, str]] = MappingProxyType({
        "app_name": EXAMPLE_ENV_KEY_APP_NAME,
        "api_key": EXAMPLE_ENV_KEY_API_KEY,
        "max_workers": EXAMPLE_ENV_KEY_MAX_WORKERS,
        "timeout": EXAMPLE_ENV_KEY_TIMEOUT,
    })
    EXAMPLE_ENV_MAP_ADVANCED_APP: Final[Mapping[str, str]] = MappingProxyType({
        "database_url": EXAMPLE_ENV_KEY_DATABASE_URL,
        "redis_url": EXAMPLE_ENV_KEY_REDIS_URL,
        "api_key": EXAMPLE_ENV_KEY_API_KEY,
        "max_workers": EXAMPLE_ENV_KEY_MAX_WORKERS,
        "enable_metrics": EXAMPLE_ENV_KEY_ENABLE_METRICS,
        "log_level": EXAMPLE_ENV_KEY_LOG_LEVEL,
        "temp_dir": EXAMPLE_ENV_KEY_TEMP_DIR,
    })

    EXAMPLE_DB_URL_PREFIXES: Final[tuple[str, str]] = (
        "postgresql://",
        "mysql://",
    )
    EXAMPLE_REDIS_URL_PREFIX: Final[str] = "redis://"
    EXAMPLE_ERR_INVALID_HOST: Final[str] = "Host must be a valid hostname or IP"
    EXAMPLE_ERR_INVALID_DB_URL: Final[str] = "DATABASE_URL must be a valid database URL"
    EXAMPLE_ERR_INVALID_REDIS_URL: Final[str] = "REDIS_URL must be a valid Redis URL"
    EXAMPLE_ERR_INVALID_EMAIL_FORMAT: Final[str] = "Invalid email format"
    EXAMPLE_ERR_PORT_RANGE_FMT: Final[str] = (
        "Port must be between {min_port} and {max_port}"
    )
    EXAMPLE_ERR_PORT_RANGE_SHORT_FMT: Final[str] = (
        "Port must be between {min_port}-{max_port}"
    )
    EXAMPLE_ERR_PORT_NUMBER: Final[str] = "Port must be a number"
    EXAMPLE_ERR_PORT_VALID_NUMBER: Final[str] = "Port must be a valid number"
    EXAMPLE_ERR_VALUE_VALID_INTEGER: Final[str] = "Value must be a valid integer"
    EXAMPLE_ERR_VALUE_VALID_NUMBER: Final[str] = "Value must be a valid number"
    EXAMPLE_ERR_SETUP_CANCELLED: Final[str] = "Setup cancelled by user"
    EXAMPLE_ERR_CONFIG_DISCARDED: Final[str] = "Configuration discarded by user"
    EXAMPLE_ERR_FAILED_COLLECT_CONFIGURATION: Final[str] = (
        "Failed to collect configuration"
    )
    EXAMPLE_ERR_FAILED_SELECT_ENVIRONMENT: Final[str] = "Failed to select environment"
    EXAMPLE_ERR_FAILED_COLLECT_HOST: Final[str] = "Failed to collect host"
    EXAMPLE_ERR_FAILED_COLLECT_PORT: Final[str] = "Failed to collect port"
    EXAMPLE_ERR_FAILED_GET_DATABASE_NAME: Final[str] = "Failed to get database name"
    EXAMPLE_ERR_FAILED_GET_PASSWORD: Final[str] = "Failed to get password"
    EXAMPLE_ERR_FAILED_LOAD_CONFIG: Final[str] = "Failed to load settings"
    EXAMPLE_ERR_CONFIG_CONTENT_MAPPING: Final[str] = "Config content must be a mapping"
    EXAMPLE_ERR_NAME_PROMPT_FAILED: Final[str] = "Name prompt failed"
    EXAMPLE_ERR_ENVIRONMENT_CHOICE_FAILED: Final[str] = "Environment choice failed"
    EXAMPLE_ERR_PORT_PROMPT_FAILED: Final[str] = "Port prompt failed"
    EXAMPLE_ERR_NO_DATA_FILE_FOUND: Final[str] = "No data file found"
    EXAMPLE_ERR_DATA_FILE_MUST_BE_MAPPING: Final[str] = (
        "Data file must contain a mapping"
    )
    EXAMPLE_ERR_NEGATIVE_VALUES_NOT_ALLOWED: Final[str] = "Negative values not allowed"
    EXAMPLE_ERR_MAX_WORKERS_MUST_BE_INTEGER: Final[str] = (
        "max_workers must be an integer"
    )

    EXAMPLE_MSG_OPERATION_COMPLETED: Final[str] = "Operation completed"
    EXAMPLE_MSG_ERROR_SOMETHING_FAILED: Final[str] = "ERROR: Something failed"

    PERF_LRU_CACHE_SIZE: Final[int] = 128
    PERF_CALC_INPUT_SIZE: Final[int] = 1_000_000
    PERF_LAZY_DATA_SIZE: Final[int] = 10_000
    PERF_TABLE_PREVIEW_SIZE: Final[int] = 10
    PERF_DEFAULT_BATCH_SIZE: Final[int] = 100
    PERF_DATASET_SIZE: Final[int] = 1_000
    PERF_ITEMS_SIZE: Final[int] = 500


c = ExamplesFlextCliConstants

__all__: list[str] = [
    "ExamplesFlextCliConstants",
    "c",
]
