"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

EXPECTED MYPY ISSUES (documented for awareness):
- None currently (CliContext moved to context.py following flext-core patterns)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Self, cast, get_args, get_origin, override

from flext_core import FlextCore
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    fields,
    model_validator,
)
from pydantic_core import PydanticUndefined

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes


class FlextCliModels(FlextCore.Models):
    """Single unified CLI models class following FLEXT standards.

    Contains all Pydantic model subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Extends FlextCore.Models foundation for ecosystem consistency
    - Uses centralized validation via FlextCore.Models.Validation
    - Implements CLI-specific extensions while reusing core functionality

    CRITICAL ARCHITECTURE: ALL model validation is centralized in FlextCore.Models.
    NO inline validation is allowed in service methods.
    """

    # For test instantiation
    name: str = Field(default="FlextCliModels")

    # Advanced Pydantic 2.11 configuration for comprehensive model behavior
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=False,
        validate_return=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        hide_input_in_errors=True,
        json_schema_extra={
            "title": "FlextCliModels",
            "description": "Comprehensive CLI domain models with advanced Pydantic 2.11 features",
            "examples": [
                {
                    "cli_command": {
                        "command_line": "flext validate",
                        "status": "pending",
                        "args": ["validate"],
                    }
                }
            ],
        },
    )

    @model_validator(mode="after")
    def validate_cli_models_consistency(self) -> Self:
        """Cross-model validation ensuring CLI models consistency."""
        # Ensure all required nested classes are properly defined
        required_nested_classes = [
            "BaseEntity",
            "BaseValidatedModel",
            "BaseConfig",
            "CliCommand",
            "DebugInfo",
            "CliSession",
        ]

        for class_name in required_nested_classes:
            if not hasattr(self.__class__, class_name):
                error_message = f"Required nested class {class_name} not found"
                raise ValueError(error_message)

        return self

    @field_serializer("model_summary")
    def serialize_model_summary(
        self, value: FlextCore.Types.StringDict, _info: object
    ) -> dict[str, str | dict[str, str | int]]:
        """Serialize model summary with additional metadata."""
        return {
            **value,
            "_metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "total_models": len(value),
                "serialization_version": "2.11",
            },
        }

    def execute(self) -> FlextCore.Result[object]:
        """Execute model operations - placeholder for testing."""
        return FlextCore.Result[object].ok(None)

    # ========================================================================
    # CLI MODEL INTEGRATION UTILITIES - Pydantic → CLI Conversion
    # ========================================================================

    class CliModelConverter:
        """Comprehensive utilities for converting Pydantic models to CLI parameters.

        Provides complete automation from Pydantic Field metadata to Click-compatible
        CLI options and arguments, enabling fully model-driven CLI development.

        ARCHITECTURAL PATTERN:
        - Extracts Pydantic Field metadata (type, default, description, validators)
        - Converts to CLI parameter specifications (option name, type, help, validation)
        - Handles type conversions: Pydantic types → Python native types → Click types
        - Supports validation, default values, and complex nested structures
        - Generates complete Click decorators and command specifications
        - Provides bidirectional conversion (Model ↔ CLI parameters)

        COMPREHENSIVE FEATURES:
        - model_to_cli_params: Extract all CLI parameters from model
        - model_to_click_options: Generate Click option decorators
        - cli_args_to_model: Validate and convert CLI args to model instance
        - generate_command_spec: Complete command specification with all metadata

        USAGE:
            # Extract CLI parameters
            params = CliModelConverter.model_to_cli_params(MyModel)

            # Generate Click options
            options = CliModelConverter.model_to_click_options(MyModel)

            # Validate and convert CLI input
            model_instance = CliModelConverter.cli_args_to_model(MyModel, cli_args)

            # Generate complete command specification
            command_spec = CliModelConverter.generate_command_spec(MyModel, "my-command")
        """

        @staticmethod
        def pydantic_type_to_python_type(field_type: type) -> type:
            """Convert Pydantic field type to Python native type.

            Handles Optional, Union, List, Dict, and complex Pydantic types,
            converting them to Python native types suitable for CLI usage.

            Args:
                field_type: Pydantic field type annotation

            Returns:
                type: Python native type for CLI usage

            """
            # Handle Optional types (Union with None)
            origin = get_origin(field_type)
            if origin is type(int | None):  # Union type check
                args = get_args(field_type)
                if args:
                    # Get first non-None type
                    for arg in args:
                        if arg is not type(None):
                            return FlextCliModels.CliModelConverter.pydantic_type_to_python_type(
                                arg
                            )

            # Handle List types
            if origin is list:
                return list

            # Handle Dict types
            if origin is dict:
                return dict

            # Native types pass through
            if field_type in {str, int, float, bool}:
                return field_type

            # Default to str for complex types
            return str

        @staticmethod
        def python_type_to_click_type(python_type: type) -> str:
            """Convert Python type to Click type specification string.

            Args:
                python_type: Python type

            Returns:
                str: Click type specification (e.g., 'STRING', 'INT', 'FLOAT', 'BOOL')

            """
            type_map = {
                str: "STRING",
                int: "INT",
                float: "FLOAT",
                bool: "BOOL",
                list: "STRING",  # Lists as comma-separated strings
                dict: "STRING",  # Dicts as JSON strings
            }
            return type_map.get(python_type, "STRING")

        @staticmethod
        def field_to_cli_param(
            field_name: str, field_info: fields.FieldInfo
        ) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Convert Pydantic Field to comprehensive CLI parameter specification.

            Args:
                field_name: Name of the field
                field_info: Pydantic FieldInfo object

            Returns:
                FlextCore.Result containing CLI parameter specification dict with:
                - name: CLI parameter name (--field-name)
                - type: Python type for the parameter
                - click_type: Click type specification
                - default: Default value if any
                - help: Help text from field description
                - required: Whether the parameter is required
                - validators: List of validation functions
                - metadata: Additional Pydantic metadata

            """
            try:
                # Extract field metadata
                field_type = field_info.annotation
                if field_type is None:
                    return FlextCore.Result[FlextCore.Types.Dict].fail(
                        f"Field {field_name} has no type annotation"
                    )

                # Convert types
                python_type = (
                    FlextCliModels.CliModelConverter.pydantic_type_to_python_type(
                        field_type
                    )
                )
                click_type = FlextCliModels.CliModelConverter.python_type_to_click_type(
                    python_type
                )

                # Determine if required (no default value)
                is_required = field_info.default is PydanticUndefined
                default_value = None if is_required else field_info.default

                # Extract description
                description = field_info.description or f"{field_name} parameter"

                # Extract validation constraints from metadata
                validators: FlextCore.Types.StringList = []
                metadata: FlextCore.Types.Dict = {}

                if hasattr(field_info, "metadata"):
                    for meta_item in field_info.metadata:
                        if hasattr(meta_item, "__dict__"):
                            metadata.update(meta_item.__dict__)

                # Build comprehensive CLI parameter spec
                cli_param: FlextCore.Types.Dict = {
                    "name": field_name.replace("_", "-"),  # CLI convention: dashes
                    "field_name": field_name,  # Original Python field name
                    "type": python_type,
                    "click_type": click_type,
                    "required": is_required,
                    "default": default_value,
                    "help": description,
                    "validators": validators,
                    "metadata": metadata,
                }

                return FlextCore.Result[FlextCore.Types.Dict].ok(cli_param)
            except Exception as e:
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    f"Failed to convert field {field_name}: {e}"
                )

        @staticmethod
        def model_to_cli_params(
            model_class: type[BaseModel],
        ) -> FlextCore.Result[list[FlextCore.Types.Dict]]:
            """Extract all fields from Pydantic model and convert to CLI parameters.

            Args:
                model_class: Pydantic model class to convert

            Returns:
                FlextCore.Result containing list of comprehensive CLI parameter specifications

            """
            try:
                cli_params: list[FlextCore.Types.Dict] = []

                # Get model fields
                model_fields = model_class.model_fields

                for field_name, field_info in model_fields.items():
                    # Convert each field
                    param_result = FlextCliModels.CliModelConverter.field_to_cli_param(
                        field_name, field_info
                    )

                    if param_result.is_failure:
                        # Skip fields that fail conversion
                        continue

                    cli_params.append(param_result.unwrap())

                return FlextCore.Result[list[FlextCore.Types.Dict]].ok(cli_params)
            except Exception as e:
                return FlextCore.Result[list[FlextCore.Types.Dict]].fail(
                    f"Failed to convert model {model_class.__name__}: {e}"
                )

        @staticmethod
        def model_to_click_options(
            model_class: type[BaseModel],
        ) -> FlextCore.Result[list[FlextCore.Types.Dict]]:
            """Generate Click option specifications from Pydantic model.

            Creates complete Click option definitions that can be used to
            programmatically create Click commands with @click.option decorators.

            Args:
                model_class: Pydantic model class to convert

            Returns:
                FlextCore.Result containing list of Click option specifications with:
                - option_name: Full option name with dashes (e.g., '--field-name')
                - param_decls: List of parameter declarations
                - type: Click type object
                - default: Default value
                - help: Help text
                - required: Whether option is required
                - show_default: Whether to show default in help

            """
            try:
                params_result = FlextCliModels.CliModelConverter.model_to_cli_params(
                    model_class
                )
                if params_result.is_failure:
                    return FlextCore.Result[list[FlextCore.Types.Dict]].fail(
                        params_result.error
                    )

                click_options: list[FlextCore.Types.Dict] = []
                for param in params_result.unwrap():
                    option_name = f"--{param['name']}"

                    click_option = {
                        "option_name": option_name,
                        "param_decls": [option_name],
                        "type": param["click_type"],
                        "default": param["default"],
                        "help": param["help"],
                        "required": param["required"],
                        "show_default": not param["required"],
                        "metadata": param.get("metadata", {}),
                    }

                    click_options.append(click_option)

                return FlextCore.Result[list[FlextCore.Types.Dict]].ok(click_options)
            except Exception as e:
                return FlextCore.Result[list[FlextCore.Types.Dict]].fail(
                    f"Failed to generate Click options for {model_class.__name__}: {e}"
                )

        @staticmethod
        def cli_args_to_model(
            model_class: type[BaseModel],
            cli_args: FlextCore.Types.Dict,
        ) -> FlextCore.Result[BaseModel]:
            """Convert CLI arguments dictionary to Pydantic model instance.

            Validates CLI input against model constraints and creates a validated
            model instance. Handles type conversions and validation errors.

            Args:
                model_class: Pydantic model class to instantiate
                cli_args: Dictionary of CLI argument name/value pairs

            Returns:
                FlextCore.Result containing validated model instance

            """
            try:
                # Convert CLI argument names (with dashes) to Python field names (with underscores)
                model_args = {
                    key.replace("-", "_"): value for key, value in cli_args.items()
                }

                # Create and validate model instance
                model_instance = model_class(**model_args)

                return FlextCore.Result[BaseModel].ok(model_instance)
            except Exception as e:
                return FlextCore.Result[BaseModel].fail(
                    f"Failed to create {model_class.__name__} from CLI args: {e}"
                )

    class CliModelDecorators:
        """Decorators for model-driven CLI command generation.

        Provides decorators that automatically generate CLI commands from Pydantic models,
        eliminating manual parameter declaration boilerplate.

        ARCHITECTURAL PATTERN:
        - Introspect Pydantic model structure
        - Generate CLI parameters from model fields
        - Inject validation before handler execution
        - Return validated model instance to handler

        USAGE:
            @cli_from_model(ConfigModel)
            def configure(config: ConfigModel):
                # config is already validated Pydantic instance
                pass
        """

        @staticmethod
        def cli_from_model(
            model_class: type[BaseModel], command_name: str | None = None
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator that generates CLI command from Pydantic model.

            Args:
                model_class: Pydantic model class defining CLI parameters
                command_name: Optional command name (defaults to function name)

            Returns:
                Decorator function that wraps the command handler

            Example:
                @cli_from_model(DatabaseConfig)
                def setup_database(config: DatabaseConfig):
                    # config is validated DatabaseConfig instance
                    print(f"Connecting to {config.host}:{config.port}")

            """

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                # Store model metadata on function for CLI builder inspection
                setattr(func, "__cli_model__", model_class)
                setattr(func, "__cli_command_name__", command_name or func.__name__)

                def wrapper(**cli_kwargs: object) -> object:
                    # Validate CLI input with Pydantic model
                    validation_result = (
                        FlextCliModels.CliModelConverter.cli_args_to_model(
                            model_class, cli_kwargs
                        )
                    )

                    if validation_result.is_failure:
                        # Return error result
                        return FlextCore.Result[object].fail(
                            f"Invalid input: {validation_result.error}"
                        )

                    validated_model = validation_result.unwrap()

                    # Call original function with validated model
                    return func(validated_model)

                return wrapper

            return decorator

        @staticmethod
        def cli_from_multiple_models(
            *model_classes: type[BaseModel], command_name: str | None = None
        ) -> Callable[[Callable[..., object]], Callable[..., object]]:
            """Decorator for CLI command with multiple model inputs.

            Args:
                *model_classes: Multiple Pydantic model classes
                command_name: Optional command name

            Returns:
                Decorator function that validates with all models

            Example:
                @cli_from_multiple_models(AuthConfig, ServerConfig)
                def deploy(auth: AuthConfig, server: ServerConfig):
                    # Both configs are validated instances
                    pass

            """

            def decorator(func: Callable[..., object]) -> Callable[..., object]:
                # Store multiple models metadata
                setattr(func, "__cli_models__", model_classes)
                setattr(func, "__cli_command_name__", command_name or func.__name__)

                def wrapper(**cli_kwargs: object) -> object:
                    validated_models: list[BaseModel] = []

                    # Validate with each model
                    for model_class in model_classes:
                        validation_result = (
                            FlextCliModels.CliModelConverter.cli_args_to_model(
                                model_class, cli_kwargs
                            )
                        )

                        if validation_result.is_failure:
                            return FlextCore.Result[object].fail(
                                f"Validation failed for {model_class.__name__}: {validation_result.error}"
                            )

                        validated_models.append(validation_result.unwrap())

                    # Call with validated models
                    return func(*validated_models)

                return wrapper

            return decorator

    # Base classes for common functionality - using flext-core patterns
    class BaseEntity(FlextCore.Models.Entity, FlextCliMixins.ValidationMixin):
        """Base entity with common fields for entities with id, timestamps, and status."""

        model_config = ConfigDict(
            validate_assignment=True,
            use_enum_values=True,
            arbitrary_types_allowed=True,
            extra="forbid",
            validate_return=True,
        )

        id: str = Field(
            default_factory=lambda: f"entity_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
        updated_at: datetime | None = (
            None  # Inherit from parent - can be None initially
        )
        status: str = Field(default="pending")

        @computed_field
        def entity_age_seconds(self) -> float:
            """Computed field for entity age in seconds."""
            return (datetime.now(UTC) - self.created_at).total_seconds()

        @model_validator(mode="after")
        def validate_timestamps(self) -> Self:
            """Validate timestamp consistency."""
            if self.updated_at and self.updated_at < self.created_at:
                timestamp_error = "updated_at cannot be before created_at"
                raise ValueError(timestamp_error)
            return self

        def update_timestamp(self) -> None:
            """Update the updated_at timestamp."""
            self.updated_at = datetime.now(UTC)

    class BaseValidatedModel(
        FlextCore.Models.StrictArbitraryTypesModel, FlextCliMixins.ValidationMixin
    ):
        """Base model with common validation patterns."""

        @computed_field
        def model_type(self) -> str:
            """Computed field returning the model type name."""
            return self.__class__.__name__

    class BaseConfig(BaseValidatedModel):
        """Base configuration model with common config validation patterns."""

        @model_validator(mode="after")
        def validate_config_consistency(self) -> Self:
            """Validate configuration consistency."""
            # Base validation for all config models
            return self

    class CliCommand(BaseEntity, FlextCliMixins.BusinessRulesMixin):
        """CLI command model extending _BaseEntity."""

        command_line: str = Field(min_length=1)
        args: FlextCore.Types.StringList = Field(default_factory=list)
        exit_code: int | None = None
        output: str = Field(default="")
        error_output: str = Field(default="")
        name: str = Field(default="")
        description: str = Field(default="")
        usage: str = Field(default="")
        entry_point: str = Field(default="")
        plugin_version: str = Field(default="default")
        # status field inherited from _BaseEntity

        @computed_field
        def command_summary(self) -> FlextCore.Types.Dict:
            """Computed field for command execution summary."""
            return {
                "command": self.command_line,
                "args_count": len(self.args),
                "has_output": bool(self.output),
                "has_errors": bool(self.error_output),
                "is_completed": self.exit_code is not None,
                "execution_time": self.entity_age_seconds,
            }

        @computed_field
        def is_successful(self) -> bool:
            """Computed field indicating if command executed successfully."""
            return self.exit_code == 0 if self.exit_code is not None else False

        @model_validator(mode="after")
        def validate_command_consistency(self) -> Self:
            """Cross-field validation for command consistency."""
            # If exit_code is set, status should be completed
            if (
                self.exit_code is not None
                and self.status == FlextCliConstants.CommandStatus.PENDING.value
            ):
                exit_code_error = "Command with exit_code cannot have pending status"
                raise ValueError(exit_code_error)

            # If command has output, it should have been executed
            if (
                self.output
                and self.status == FlextCliConstants.CommandStatus.PENDING.value
            ):
                output_error = "Command with output cannot have pending status"
                raise ValueError(output_error)

            return self

        @field_serializer("command_line")
        def serialize_command_line(self, value: str, _info: object) -> str:
            """Serialize command line with safety checks for sensitive commands."""
            # Mask potentially sensitive command parts
            sensitive_patterns = [
                FlextCliConstants.DictKeys.PASSWORD,
                FlextCliConstants.DictKeys.TOKEN,
                "secret",
                "key",
            ]
            for pattern in sensitive_patterns:
                if pattern in value.lower():
                    return value.replace(pattern, "*" * len(pattern))
            return value

        @classmethod
        def validate_command_input(
            cls, data: FlextCliTypes.Data.CliCommandData | None
        ) -> FlextCore.Result[FlextCliTypes.Data.CliCommandData | None]:
            """Validate and normalize command input data using railway pattern.

            Args:
                data: Command input data to validate

            Returns:
                FlextCore.Result with validated and normalized data

            """
            # Extract command from data - ensure it's a string
            if not isinstance(data, dict):
                return FlextCore.Result[FlextCliTypes.Data.CliCommandData | None].fail(
                    "Command data must be a dictionary"
                )

            command = data.pop("command")
            if not isinstance(command, str):
                return FlextCore.Result[FlextCliTypes.Data.CliCommandData | None].fail(
                    "Command must be a string"
                )

            # Normalize command data
            normalized_data = {
                "command": command,
                "execution_time": data.get("execution_time"),
                **{k: v for k, v in data.items() if k != "command"},
            }

            return FlextCore.Result[FlextCliTypes.Data.CliCommandData | None].ok(
                normalized_data
            )

        def validate_business_rules(self) -> FlextCore.Result[None]:
            """Validate command business rules."""
            # Use mixin validation methods
            command_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Command line", self.command_line
            )
            if not command_result.is_success:
                return command_result

            status_result = FlextCliMixins.ValidationMixin.validate_status(self.status)
            if not status_result.is_success:
                return status_result

            return FlextCore.Result[None].ok(None)

        def start_execution(self) -> FlextCore.Result[None]:
            """Start command execution."""
            state_result = (
                FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
                    self.status,
                    FlextCliConstants.CommandStatus.PENDING.value,
                    "start execution",
                )
            )
            if not state_result.is_success:
                return state_result

            self.status = FlextCliConstants.CommandStatus.RUNNING.value
            return FlextCore.Result[None].ok(None)

        def complete_execution(
            self, exit_code: int, output: str = ""
        ) -> FlextCore.Result[None]:
            """Complete command execution."""
            state_result = (
                FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
                    self.status,
                    FlextCliConstants.CommandStatus.RUNNING.value,
                    "complete execution",
                )
            )
            if not state_result.is_success:
                return state_result

            self.exit_code = exit_code
            self.output = output
            self.status = FlextCliConstants.CommandStatus.COMPLETED.value
            return FlextCore.Result[None].ok(None)

    class DebugInfo(BaseValidatedModel):
        """Debug information model extending _BaseValidatedModel."""

        service: str = Field(default="FlextCliDebug")
        status: str = Field(default="operational")
        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        system_info: FlextCore.Types.StringDict = Field(default_factory=dict)
        config_info: FlextCore.Types.StringDict = Field(default_factory=dict)
        level: str = Field(default="info")
        message: str = Field(default="")

        @computed_field
        def debug_summary(self) -> FlextCore.Types.Dict:
            """Computed field for debug information summary."""
            return {
                "service": self.service,
                "level": self.level,
                "has_system_info": bool(self.system_info),
                "has_config_info": bool(self.config_info),
                "message_length": len(self.message),
                "age_seconds": (datetime.now(UTC) - self.timestamp).total_seconds(),
            }

        @model_validator(mode="after")
        def validate_debug_consistency(self) -> Self:
            """Validate debug info consistency."""
            valid_levels = {"debug", "info", "warning", "error", "critical"}
            if self.level not in valid_levels:
                msg = f"Invalid debug level: {self.level}"
                raise ValueError(msg)
            return self

        @field_serializer("system_info", "config_info")
        def serialize_sensitive_info(
            self, value: FlextCore.Types.StringDict, _info: object
        ) -> FlextCore.Types.StringDict:
            """Serialize system/config info masking sensitive values."""
            sensitive_keys = {
                FlextCliConstants.DictKeys.PASSWORD,
                FlextCliConstants.DictKeys.TOKEN,
                "secret",
                "key",
                "auth",
            }
            return {
                k: (
                    "***MASKED***"
                    if any(sens in k.lower() for sens in sensitive_keys)
                    else v
                )
                for k, v in value.items()
            }

        def validate_business_rules(self) -> FlextCore.Result[None]:
            """Validate debug info business rules."""
            # Use mixin validation methods
            service_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Service name", self.service
            )
            if not service_result.is_success:
                return service_result

            # Validate level
            valid_levels = ["debug", "info", "warning", "error", "critical"]
            level_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                "level", self.level, valid_levels
            )
            if not level_result.is_success:
                return level_result

            return FlextCore.Result[None].ok(None)

    class CliSession(
        FlextCore.Models.Entity,
        FlextCliMixins.BusinessRulesMixin,
    ):
        """CLI session model extending FlextCore.Models.Entity."""

        # id field inherited from FlextCore.Models.Entity
        session_id: str = Field(
            default_factory=lambda: f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}"
        )
        start_time: str | None = Field(default=None)
        end_time: str | None = None
        last_activity: str | None = Field(default=None)
        duration_seconds: float = Field(default=0.0)
        commands_executed: int = Field(default=0)
        commands: list[FlextCliModels.CliCommand] = Field(default_factory=list)
        status: str = Field(default="active")
        user_id: str | None = None

        @computed_field
        def session_summary(self) -> FlextCore.Types.Dict:
            """Computed field for session activity summary."""
            return {
                "session_id": self.session_id,
                "is_active": self.status == "active",
                "commands_count": len(self.commands),
                "duration_minutes": round(self.duration_seconds / 60, 2),
                "has_user": self.user_id is not None,
                "last_activity_age": self._calculate_activity_age(),
            }

        @computed_field
        def commands_by_status(self) -> dict[str, int]:
            """Computed field grouping commands by status."""
            status_counts: dict[str, int] = {}
            for command in self.commands:
                status = command.status
                status_counts[status] = status_counts.get(status, 0) + 1
            return status_counts

        @model_validator(mode="after")
        def validate_session_consistency(self) -> Self:
            """Cross-field validation for session consistency."""
            # Commands count should match actual commands list
            if self.commands_executed != len(self.commands):
                self.commands_executed = len(self.commands)

            # Duration should be non-negative
            if self.duration_seconds < 0:
                msg = "duration_seconds cannot be negative"
                raise ValueError(msg)

            return self

        @field_serializer("commands")
        def serialize_commands(
            self, value: list[FlextCliModels.CliCommand], _info: object
        ) -> list[FlextCore.Types.Dict]:
            """Serialize commands with summary information."""
            return [
                {
                    "id": cmd.id,
                    "command_line": cmd.command_line,
                    "status": cmd.status,
                    "exit_code": cmd.exit_code,
                    "created_at": cmd.created_at.isoformat(),
                }
                for cmd in value
            ]

        def _calculate_activity_age(self) -> float | None:
            """Calculate time since last activity in seconds."""
            if not self.last_activity:
                return None
            try:
                last_time = datetime.fromisoformat(self.last_activity)
                return (datetime.now(UTC) - last_time).total_seconds()
            except (ValueError, AttributeError):
                return None

        @override
        def __init__(
            self,
            session_id: str | None = None,
            user_id: str | None = None,
            start_time: str | datetime | None = None,
            **data: Any,
        ) -> None:
            """Initialize CLI session with proper type handling.

            Args:
                session_id: Unique session identifier (optional, auto-generated if None)
                user_id: User identifier
                start_time: Session start time
                **data: Additional session data

            """
            # Set session-specific fields
            if user_id is not None:
                data["user_id"] = user_id
            if start_time is not None:
                # Convert datetime to string if needed
                if isinstance(start_time, datetime):
                    data["start_time"] = start_time.isoformat()
                else:
                    data["start_time"] = start_time

            # Call parent constructor with proper data
            # Ensure required fields have correct types for parent class
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            if "version" not in data:
                data["version"] = 1
            if "created_at" not in data:
                data["created_at"] = datetime.now(UTC)
            if "updated_at" not in data:
                data["updated_at"] = None
            if "domain_events" not in data:
                data["domain_events"] = []

            # Create parent class with explicit parameters
            version_obj = data.get("version", 1)
            version_value: int = version_obj if isinstance(version_obj, int) else 1

            created_at_obj = data.get("created_at", datetime.now(UTC))
            created_at_value: datetime = (
                created_at_obj
                if isinstance(created_at_obj, datetime)
                else datetime.now(UTC)
            )

            updated_at_obj = data.get("updated_at")
            updated_at_value: datetime | None = (
                updated_at_obj if isinstance(updated_at_obj, datetime) else None
            )

            domain_events_obj = data.get("domain_events", [])
            domain_events_value: FlextCore.Types.List = (
                domain_events_obj if isinstance(domain_events_obj, list) else []
            )

            super().__init__(
                id=str(data.get("id", str(uuid.uuid4()))),
                version=version_value,
                created_at=created_at_value,
                updated_at=updated_at_value,
                domain_events=cast(
                    "list[FlextCore.Models.DomainEvent]", domain_events_value
                ),
            )

            # Set session identifier (auto-generate if not provided)
            if session_id is not None:
                self.session_id = session_id

        def validate_business_rules(self) -> FlextCore.Result[None]:
            """Validate session business rules."""
            # Use mixin validation methods
            session_id_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Session ID", self.session_id
            )
            if not session_id_result.is_success:
                return session_id_result

            # Validate user_id if provided
            if self.user_id is not None and not self.user_id.strip():
                return FlextCore.Result[None].fail(
                    FlextCliConstants.ErrorMessages.USER_ID_EMPTY
                )

            valid_statuses = ["active", "completed", "terminated"]
            status_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                "status", self.status, valid_statuses
            )
            if not status_result.is_success:
                return status_result

            return FlextCore.Result[None].ok(None)

        def add_command(
            self, command: FlextCliModels.CliCommand
        ) -> FlextCore.Result[None]:
            """Add a command to the session.

            Args:
                command: Command to add to the session

            Returns:
                FlextCore.Result[None]: Success if command added, failure otherwise

            """
            try:
                # Add command to the commands list
                self.commands.append(command)

                # Update commands executed count
                self.commands_executed = len(self.commands)

                return FlextCore.Result[None].ok(None)
            except Exception as e:
                return FlextCore.Result[None].fail(
                    f"Failed to add command to session: {e}"
                )

    class LoggingConfig(BaseValidatedModel):
        """Logging configuration model for CLI operations."""

        log_level: str = Field(...)
        log_format: str = Field(...)
        console_output: bool = Field(default=False)
        log_file: str | None = Field(default=None)

        @computed_field
        def logging_summary(self) -> FlextCore.Types.Dict:
            """Computed field returning summary of logging configuration."""
            return {
                "level": self.log_level,
                "format": self.log_format,
                "console_output": self.console_output,
                "log_file": self.log_file,
            }


__all__ = [
    "FlextCliModels",
]
