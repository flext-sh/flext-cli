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
from typing import Self, cast, get_args, get_origin, override

from flext_core import FlextCore
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    fields,
    model_validator,
)
from pydantic_core import PydanticUndefined

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes

logger = FlextCore.Logger(__name__)


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
    # PHASE 7-8: Runtime type & Pydantic enforcement with strict validation
    model_config = ConfigDict(
        validate_assignment=True,  # Validate on field assignment
        validate_return=True,  # Validate return values
        validate_default=True,  # Phase 8: Validate default values
        strict=True,  # Strict type coercion (Phase 7 - no implicit conversions)
        str_strip_whitespace=True,  # Phase 8: Auto-strip whitespace from strings
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid",  # No extra fields allowed
        frozen=False,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        hide_input_in_errors=True,
        json_schema_extra={
            "title": "FlextCliModels",
            "description": "Comprehensive CLI domain models with enhanced runtime validation (Phases 7-8)",
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
            type_map: dict[type, str] = {
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
        ) -> FlextCore.Result[FlextCliModels.CliParameterSpec]:
            """Convert Pydantic Field to comprehensive CLI parameter specification.

            Args:
                field_name: Name of the field
                field_info: Pydantic FieldInfo object

            Returns:
                FlextCore.Result containing CLI parameter specification dict[str, object] with:
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
                    return FlextCore.Result[FlextCliModels.CliParameterSpec].fail(
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
                validators: list[object] = []
                metadata: FlextCore.Types.Dict = {}

                if hasattr(field_info, "metadata"):
                    for meta_item in field_info.metadata:
                        if hasattr(meta_item, "__dict__"):
                            metadata.update(meta_item.__dict__)

                # Build comprehensive CLI parameter spec
                cli_param = FlextCliModels.CliParameterSpec(
                    name=field_name.replace("_", "-"),  # CLI convention: dashes
                    field_name=field_name,  # Original Python field name
                    param_type=python_type,
                    click_type=click_type,
                    required=is_required,
                    default=default_value,
                    help=description,
                    validators=validators,
                    metadata=metadata,
                )

                return FlextCore.Result[FlextCliModels.CliParameterSpec].ok(cli_param)
            except Exception as e:
                return FlextCore.Result[FlextCliModels.CliParameterSpec].fail(
                    f"Failed to convert field {field_name}: {e}"
                )

        @staticmethod
        def model_to_cli_params(
            model_class: type[BaseModel],
        ) -> FlextCore.Result[list[FlextCliModels.CliParameterSpec]]:
            """Extract all fields from Pydantic model and convert to CLI parameters.

            Args:
                model_class: Pydantic model class to convert

            Returns:
                FlextCore.Result containing list of comprehensive CLI parameter specifications

            """
            try:
                cli_params: list[FlextCliModels.CliParameterSpec] = []

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

                return FlextCore.Result[list[FlextCliModels.CliParameterSpec]].ok(
                    cli_params
                )
            except Exception as e:
                return FlextCore.Result[list[FlextCliModels.CliParameterSpec]].fail(
                    f"Failed to convert model {model_class.__name__}: {e}"
                )

        @staticmethod
        def model_to_click_options(
            model_class: type[BaseModel],
        ) -> FlextCore.Result[list[FlextCliModels.CliOptionSpec]]:
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
                    return FlextCore.Result[list[FlextCliModels.CliOptionSpec]].fail(
                        params_result.error
                    )

                click_options: list[FlextCliModels.CliOptionSpec] = []
                for param in params_result.unwrap():
                    option_name = f"--{param.name}"

                    # Create CliOptionSpec instance
                    click_option = FlextCliModels.CliOptionSpec(
                        option_name=option_name,
                        param_decls=[option_name],
                        type=param.click_type,
                        default=param.default,
                        help=param.help,
                        required=param.required,
                        show_default=not param.required,
                        metadata=param.metadata,
                    )

                    click_options.append(click_option)

                return FlextCore.Result[list[FlextCliModels.CliOptionSpec]].ok(
                    click_options
                )
            except Exception as e:
                return FlextCore.Result[list[FlextCliModels.CliOptionSpec]].fail(
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

    # =========================================================================
    # CLI DOMAIN MODELS - Using FlextCore.Models base classes directly
    # =========================================================================

    class CliCommand(FlextCore.Models.Entity, FlextCliMixins.BusinessRulesMixin):
        """CLI command model with comprehensive CLI execution tracking.

        Extends FlextCore.Models.Entity (provides id, created_at, updated_at, version, domain_events).
        Adds CLI-specific fields for command execution, output tracking, and plugin metadata.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        - model_validator for cross-field validation
        """

        # CLI-specific fields (id, created_at, updated_at inherited from Entity)
        command_line: str = Field(
            min_length=1,
            description="Full command line string that was executed",
            examples=["flext validate", "flext deploy --env production"],
        )
        args: FlextCore.Types.StringList = Field(
            default_factory=list,
            description="Parsed command line arguments as list",
            examples=[["validate"], ["deploy", "--env", "production"]],
        )
        status: str = Field(
            default="pending",
            description="Current execution status of the command",
            examples=["pending", "running", "completed", "failed"],
        )
        exit_code: int | None = Field(
            default=None,
            description="Process exit code (0 for success, non-zero for errors)",
            examples=[0, 1, 127],
        )
        output: str = Field(
            default="",
            description="Standard output captured from command execution",
        )
        error_output: str = Field(
            default="",
            description="Standard error output captured from command execution",
        )
        execution_time: float | None = Field(
            default=None,
            ge=0.0,
            description="Command execution time in seconds",
            examples=[0.123, 5.678, 120.5],
        )
        result: FlextCliTypes.Data.CliDataDict | None = Field(
            default=None,
            description="Structured result data from command execution",
        )
        kwargs: FlextCliTypes.Data.CliDataDict = Field(
            default_factory=dict,
            description="Additional keyword arguments passed to command",
        )
        name: str = Field(
            default="",
            description="Command name or identifier",
            examples=["validate", "deploy", "test"],
        )
        description: str = Field(
            default="",
            description="Human-readable command description",
        )
        usage: str = Field(
            default="",
            description="Command usage documentation",
        )
        entry_point: str = Field(
            default="",
            description="Plugin or module entry point for this command",
        )
        plugin_version: str = Field(
            default="default",
            description="Version of the plugin providing this command",
        )

        # Pydantic 2.11 field validators for business logic validation
        @field_validator("command_line")
        @classmethod
        def validate_command_line_not_empty(cls, v: str) -> str:
            """Validate command line is not empty."""
            if not v or not v.strip():
                msg = "Command line cannot be empty"
                raise ValueError(msg)
            return v.strip()

        @field_validator("status")
        @classmethod
        def validate_status_allowed(cls, v: str) -> str:
            """Validate status is one of the allowed values."""
            allowed_statuses = {
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
            }
            if v not in allowed_statuses:
                msg = f"Invalid status '{v}'. Must be one of: {', '.join(sorted(allowed_statuses))}"
                raise ValueError(msg)
            return v

        # Pydantic 2.11 computed fields for derived properties
        @computed_field
        def is_completed(self) -> bool:
            """Check if command execution is completed."""
            return self.status == "completed"

        @computed_field
        def is_failed(self) -> bool:
            """Check if command execution failed."""
            return self.status == "failed"

        @computed_field
        def has_result(self) -> bool:
            """Check if command has result data."""
            return self.result is not None and len(self.result) > 0

        @computed_field
        def is_successful(self) -> bool:
            """Check if command executed successfully (exit code 0)."""
            return self.exit_code == 0 if self.exit_code is not None else False

        @computed_field
        def command_summary(self) -> FlextCliTypes.Data.CliDataDict:
            """Comprehensive command execution summary."""
            return {
                "command": self.command_line,
                "args_count": len(self.args),
                "has_output": bool(self.output),
                "has_errors": bool(self.error_output),
                "is_completed": cast("bool", self.is_completed),
                "is_successful": cast("bool", self.is_successful),
                "execution_time": self.execution_time,
                "status": self.status,
            }

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
            normalized_data: FlextCliTypes.Data.CliDataDict = {
                "command": command,
                "execution_time": data.get("execution_time"),
                **{k: v for k, v in data.items() if k != "command"},
            }

            # Return normalized data (type is already correct)
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

    class DebugInfo(
        FlextCore.Models.StrictArbitraryTypesModel, FlextCliMixins.ValidationMixin
    ):
        """Debug information model with comprehensive diagnostic data.

        Extends FlextCore.Models.StrictArbitraryTypesModel for strict validation.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        - field_serializer for sensitive data masking
        """

        service: str = Field(
            default="FlextCliDebug",
            description="Service name generating debug info",
            examples=["FlextCliDebug", "FlextCliCore", "FlextCliCommands"],
        )
        status: str = Field(
            default="operational",
            description="Current operational status",
            examples=["operational", "degraded", "error"],
        )
        timestamp: datetime = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Timestamp when debug info was captured (UTC)",
        )
        system_info: FlextCore.Types.StringDict = Field(
            default_factory=dict,
            description="System information and environment details",
        )
        config_info: FlextCore.Types.StringDict = Field(
            default_factory=dict,
            description="Configuration information (sensitive data masked)",
        )
        level: str = Field(
            default="info",
            description="Debug information level",
            examples=["debug", "info", "warning", "error", "critical"],
        )
        message: str = Field(
            default="",
            description="Human-readable debug message",
        )

        # Pydantic 2.11 field validators
        @field_validator("level")
        @classmethod
        def validate_level_allowed(cls, v: str) -> str:
            """Validate level is one of the allowed values."""
            valid_levels = {"debug", "info", "warning", "error", "critical"}
            if v not in valid_levels:
                msg = f"Invalid debug level '{v}'. Must be one of: {', '.join(sorted(valid_levels))}"
                raise ValueError(msg)
            return v

        # Pydantic 2.11 computed fields
        @computed_field
        def total_stats(self) -> int:
            """Total count of diagnostic statistics."""
            return len(self.system_info) + len(self.config_info)

        @computed_field
        def has_diagnostics(self) -> bool:
            """Check if debug info contains diagnostic data."""
            return bool(self.system_info) or bool(self.config_info)

        @computed_field
        def age_seconds(self) -> float:
            """Age of debug info in seconds since capture."""
            return (datetime.now(UTC) - self.timestamp).total_seconds()

        @computed_field
        def debug_summary(self) -> FlextCliModels.CliDebugData:
            """Comprehensive debug information summary."""
            return FlextCliModels.CliDebugData(
                service=self.service,
                level=self.level,
                status=self.status,
                has_system_info=bool(self.system_info),
                has_config_info=bool(self.config_info),
                total_stats=len(self.system_info)
                + len(self.config_info),  # Compute directly
                message_length=len(self.message),
                age_seconds=(
                    datetime.now(UTC) - self.timestamp
                ).total_seconds(),  # Compute directly
            )

        @model_validator(mode="after")
        def validate_debug_consistency(self) -> Self:
            """Enhanced cross-field validation for debug info consistency."""
            # Level-specific validation using FlextCore.Models.Validation
            if self.level in {"error", "critical"} and not self.message:
                msg = f"Debug level '{self.level}' requires a descriptive message"
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
        """CLI session model with comprehensive session tracking.

        Extends FlextCore.Models.Entity (provides id, created_at, updated_at, version, domain_events).
        Tracks CLI session lifecycle, command execution history, and user activity.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        - model_validator for cross-field validation
        """

        # Session-specific fields (id, created_at, updated_at inherited from Entity)
        session_id: str = Field(
            default_factory=lambda: f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}",
            description="Unique session identifier with timestamp",
            examples=["session_20250113_143022_123456"],
        )
        start_time: str | None = Field(
            default=None,
            description="Session start time in ISO 8601 format",
            examples=["2025-01-13T14:30:22Z"],
        )
        end_time: str | None = Field(
            default=None,
            description="Session end time in ISO 8601 format",
            examples=["2025-01-13T15:45:30Z"],
        )
        last_activity: str | None = Field(
            default=None,
            description="Last activity timestamp in ISO 8601 format",
            examples=["2025-01-13T15:30:00Z"],
        )
        internal_duration_seconds: float = Field(
            default=0.0,
            ge=0.0,
            description="Internal duration tracking field (use duration_seconds computed field)",
            alias="duration_seconds",
        )
        commands_executed: int = Field(
            default=0,
            ge=0,
            description="Total number of commands executed in this session",
        )
        commands: list[FlextCliModels.CliCommand] = Field(
            default_factory=list,
            description="List of commands executed in this session",
        )
        status: str = Field(
            default="active",
            description="Current session status",
            examples=["active", "inactive", "terminated"],
        )
        user_id: str | None = Field(
            default=None,
            description="User identifier associated with this session",
        )

        # Pydantic 2.11 computed fields
        @computed_field
        @property
        def duration_seconds(self) -> float:
            """Session duration in seconds (computed from start/end time)."""
            if self.start_time and self.end_time:
                try:
                    start = datetime.fromisoformat(self.start_time)
                    end = datetime.fromisoformat(self.end_time)
                    return (end - start).total_seconds()
                except (ValueError, AttributeError):
                    pass
            return self.internal_duration_seconds

        @computed_field
        def is_active(self) -> bool:
            """Check if session is currently active."""
            return self.status == "active"

        @computed_field
        def session_summary(self) -> FlextCliModels.CliSessionData:
            """Computed field for session activity summary."""
            return FlextCliModels.CliSessionData(
                session_id=self.session_id,
                is_active=self.status == "active",
                commands_count=len(self.commands),
                duration_minutes=round(self.duration_seconds / 60, 2),
                has_user=self.user_id is not None,
                last_activity_age=self._calculate_activity_age(),
            )

        @computed_field
        def commands_by_status(self) -> FlextCore.Types.IntDict:
            """Computed field grouping commands by status."""
            status_counts: FlextCore.Types.IntDict = {}
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
            **data: object,
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
            # Type guard: isinstance check ensures correct type
            if isinstance(domain_events_obj, list):
                domain_events_value: list[object] = domain_events_obj
            else:
                domain_events_value = []

            super().__init__(
                id=str(data.get("id", str(uuid.uuid4()))),
                version=version_value,
                created_at=created_at_value,
                updated_at=updated_at_value,
                domain_events=domain_events_value,  # Type narrowed by isinstance check above
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

    class LoggingConfig(
        FlextCore.Models.ArbitraryTypesModel, FlextCliMixins.ValidationMixin
    ):
        """Logging configuration model for CLI operations.

        Extends FlextCore.Models.ArbitraryTypesModel for flexible configuration.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        """

        log_level: str = Field(
            ...,
            description="Logging level for CLI operations",
            examples=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        log_format: str = Field(
            ...,
            description="Log message format string",
            examples=["%(levelname)s: %(message)s", "json", "plain"],
        )
        console_output: bool = Field(
            default=False,
            description="Enable console output for logs",
        )
        log_file: str | None = Field(
            default=None,
            description="Optional file path for persistent logging",
            examples=["/var/log/flext-cli.log", "~/.flext/cli.log"],
        )

        # Pydantic 2.11 field validators
        @field_validator("log_level")
        @classmethod
        def validate_log_level_value(cls, v: str) -> str:
            """Validate log level using FlextCore.Config reusable validator."""
            return FlextCore.Config.validate_log_level_field(v)

        # Pydantic 2.11 computed fields
        @computed_field
        @property
        def has_file_output(self) -> bool:
            """Check if file logging is enabled."""
            return self.log_file is not None and len(self.log_file) > 0

        @computed_field
        @property
        def logging_summary(self) -> FlextCliModels.CliLoggingData:
            """Comprehensive logging configuration summary."""
            return FlextCliModels.CliLoggingData(
                level=self.log_level,
                format=self.log_format,
                console_output=self.console_output,
                log_file=self.log_file,
                has_file_output=self.has_file_output,
            )

    # NOTE: CliConfig has been moved to config.py as FlextCliConfig
    # Import from flext_cli.config instead of using this duplicate

    # ========================================================================
    # DICT REPLACEMENT MODELS - Replace dict/Dict usage with proper Pydantic models
    # ========================================================================

    class CliParameterSpec(FlextCore.Models.StrictArbitraryTypesModel):
        """CLI parameter specification model - replaces dict in CLI parameter handling.

        Provides structured validation for CLI parameter specifications used in
        model-to-CLI conversion utilities.
        """

        name: str = Field(description="CLI parameter name (e.g., '--field-name')")
        field_name: str = Field(description="Original Python field name")
        param_type: type = Field(description="Python type for the parameter")
        click_type: str = Field(description="Click type specification")
        required: bool = Field(description="Whether the parameter is required")
        default: object | None = Field(default=None, description="Default value if any")
        help: str = Field(description="Help text from field description")
        validators: list[object] = Field(
            default_factory=list, description="List of validation functions"
        )
        metadata: dict[str, object] = Field(
            default_factory=dict, description="Additional Pydantic metadata"
        )

    class CliOptionSpec(FlextCore.Models.StrictArbitraryTypesModel):
        """Click option specification model - replaces dict[str, object] in Click option generation.

        Provides structured validation for Click option specifications generated
        from Pydantic model fields.
        """

        option_name: str = Field(description="Full option name with dashes")
        param_decls: list[str] = Field(description="Parameter declarations")
        type: str = Field(description="Click type object")
        default: object | None = Field(default=None, description="Default value")
        help: str = Field(description="Help text")
        required: bool = Field(description="Whether option is required")
        show_default: bool = Field(description="Whether to show default in help")
        metadata: dict[str, object] = Field(
            default_factory=dict, description="Additional metadata"
        )

    class CliCommandResult(FlextCore.Models.StrictArbitraryTypesModel):
        """CLI command result model - replaces dict[str, object] in command execution results.

        Provides structured validation for command execution results and metadata.
        """

        id: str = Field(description="Command unique identifier")
        command_line: str = Field(description="Full command line executed")
        status: str = Field(description="Command execution status")
        exit_code: int | None = Field(default=None, description="Process exit code")
        created_at: str = Field(description="Command creation timestamp")
        execution_time: float | None = Field(
            default=None, description="Execution time in seconds"
        )

    class CliDebugData(FlextCore.Models.StrictArbitraryTypesModel):
        """CLI debug data model - replaces dict[str, object] in debug information.

        Provides structured validation for debug information and diagnostic data.
        """

        service: str = Field(description="Service name generating debug info")
        level: str = Field(description="Debug information level")
        status: str = Field(description="Current operational status")
        has_system_info: bool = Field(description="Whether system info is available")
        has_config_info: bool = Field(description="Whether config info is available")
        total_stats: int = Field(description="Total count of diagnostic statistics")
        message_length: int = Field(description="Length of debug message")
        age_seconds: float = Field(description="Age of debug info in seconds")

    class CliSessionData(FlextCore.Models.StrictArbitraryTypesModel):
        """CLI session data model - replaces dict[str, object] in session summaries.

        Provides structured validation for session summary information.
        """

        session_id: str = Field(description="Unique session identifier")
        is_active: bool = Field(description="Whether session is active")
        commands_count: int = Field(description="Number of commands executed")
        duration_minutes: float = Field(description="Session duration in minutes")
        has_user: bool = Field(description="Whether session has associated user")
        last_activity_age: float | None = Field(
            default=None, description="Time since last activity"
        )

    class CliLoggingData(FlextCore.Models.ArbitraryTypesModel):
        """CLI logging data model - replaces dict[str, object] in logging summaries.

        Provides structured validation for logging configuration summaries.
        """

        level: str = Field(description="Logging level")
        format: str = Field(description="Log message format")
        console_output: bool = Field(description="Console output enabled")
        log_file: str | None = Field(default=None, description="Log file path")
        has_file_output: bool = Field(description="File logging enabled")


__all__ = [
    "FlextCliModels",
]
