"""Type definitions for flext-cli test fixtures using Python 3.13 patterns.

Module functionality: Centralized TypedDict definitions for test fixtures.
Provides type-safe configuration dictionaries replacing generic dict[str, object].

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypedDict


class GenericFieldsDict(TypedDict, total=False):
    """Generic dictionary for field validation in helpers."""


class GenericTestCaseDict(TypedDict, total=False):
    """Generic test case dictionary for helper deduplication."""


class GenericCallableParameterDict(TypedDict, total=False):
    """Generic dictionary parameter for callable operations in helpers."""


class CliPromptTestCaseDict(TypedDict, total=False):
    """CLI prompt test case data."""

    prompt_type: str
    message: str
    expected_value: str
    user_input: str
    validation_error: str
    options: list[str]
    default_value: str


class CliTypeTestDataDict(TypedDict, total=False):
    """CLI type/click type test data."""

    type_name: str
    input_value: str | int | float | bool
    expected_output: str
    is_valid: bool
    error_message: str
    attributes: dict[str, object]


class FileMetadataDict(TypedDict, total=False):
    """File metadata for file tools testing."""

    total: int
    count: int
    size: int
    modified: str
    created: str
    version: str


class ConfigDataDict(TypedDict, total=False):
    """Configuration data for testing."""

    host: str
    port: int
    debug: bool
    log_level: str
    timeout: int
    retry_count: int
    ssl_enabled: bool


class DatabaseConfigDict(TypedDict, total=False):
    """Database configuration."""

    database: str
    host: str
    port: int
    username: str
    password: str
    pool_size: int
    max_overflow: int


class AppDataDict(TypedDict, total=False):
    """Application data dictionary."""

    app: dict[str, object]
    config: dict[str, object]
    database: dict[str, object]
    metadata: dict[str, object]
    version: str


class TypeTestDataDict(TypedDict, total=False):
    """Type testing data."""

    value: str | int | float | bool | list[object] | dict[str, object] | None
    expected_type: str
    is_valid: bool
    error_message: str


class PromptConfigDict(TypedDict, total=False):
    """Prompt configuration."""

    prompt_type: str
    message: str
    choices: list[str]
    default: str
    required: bool
    validate: bool


class ClickTypeParamDict(TypedDict, total=False):
    """Click type parameter data."""

    name: str
    param_type: str
    default: str | int | bool | None
    required: bool
    help_text: str
    multiple: bool


class PipelineStepDataDict(TypedDict, total=False):
    """Pipeline step test data."""

    step_name: str
    input_value: str | int | float | bool | list[object] | dict[str, object] | None
    expected_output: str | int | float | bool | list[object] | dict[str, object] | None
    should_succeed: bool


class ValidationRuleDict(TypedDict, total=False):
    """Validation rule data."""

    field_name: str
    rule_type: str
    rule_value: str | int | bool
    is_valid: bool
    error_message: str


class MixinBehaviorDict(TypedDict, total=False):
    """Mixin behavior test data."""

    mixin_type: str
    method_name: str
    input_data: dict[str, object]
    expected_output: str | int | bool
    error_expected: bool


__all__ = [
    "AppDataDict",
    "CliPromptTestCaseDict",
    "CliTypeTestDataDict",
    "ClickTypeParamDict",
    "ConfigDataDict",
    "DatabaseConfigDict",
    "FileMetadataDict",
    "GenericCallableParameterDict",
    "GenericFieldsDict",
    "GenericTestCaseDict",
    "MixinBehaviorDict",
    "PipelineStepDataDict",
    "PromptConfigDict",
    "TypeTestDataDict",
    "ValidationRuleDict",
]
