"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Self, get_args, get_origin, override

from flext_core import (
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)
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

from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes


class FlextCliModels(FlextModels):
    """Single unified CLI models class following FLEXT standards.

    Contains all Pydantic model subclasses for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Extends FlextModels foundation for ecosystem consistency
    - Uses centralized validation via FlextModels.Validation
    - Implements CLI-specific extensions while reusing core functionality

    CRITICAL ARCHITECTURE: ALL model validation is centralized in FlextModels.
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

    @computed_field
    def active_models_count(self) -> int:
        """Computed field returning the number of active CLI model types."""
        # Count all nested model classes
        # Note: FormatOptions and CliPipeline removed - delegated to specialized services
        model_classes = [
            "CliCommand",
            "DebugInfo",
            "CliSession",
            "CliFormatters",
            "LoggingConfig",
            "PipelineConfig",
        ]
        return len(model_classes)

    @computed_field
    def model_summary(self) -> FlextTypes.StringDict:
        """Computed field returning a summary of all available models."""
        # Note: FormatOptions and CliPipeline removed - delegated to specialized services
        return {
            "CliCommand": "Command execution model with status tracking",
            "DebugInfo": "Debug information model with system details",
            "CliSession": "User session tracking model",
            "CliFormatters": "Available output formatters",
            "LoggingConfig": "Logging configuration model",
            "PipelineConfig": "Pipeline configuration model",
        }

    @model_validator(mode="after")
    def validate_cli_models_consistency(self) -> Self:
        """Cross-model validation ensuring CLI models consistency."""
        # Ensure all required nested classes are properly defined
        # Note: FormatOptions and CliPipeline removed - delegated to specialized services
        required_nested_classes = [
            "_BaseEntity",
            "_BaseValidatedModel",
            "_BaseConfig",
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
        self, value: FlextTypes.StringDict, _info: object
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
        - model_to_cli_dict: Convert model instance to CLI argument dictionary
        - validate_cli_input: Validate CLI input against model constraints

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
        ) -> FlextResult[dict[str, Any]]:
            """Convert Pydantic Field to comprehensive CLI parameter specification.

            Args:
                field_name: Name of the field
                field_info: Pydantic FieldInfo object

            Returns:
                FlextResult containing CLI parameter specification dict with:
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
                    return FlextResult[dict[str, Any]].fail(
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
                validators: list[str] = []
                metadata: dict[str, Any] = {}

                if hasattr(field_info, "metadata"):
                    for meta_item in field_info.metadata:
                        if hasattr(meta_item, "__dict__"):
                            metadata.update(meta_item.__dict__)

                # Build comprehensive CLI parameter spec
                cli_param: dict[str, Any] = {
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

                return FlextResult[dict[str, Any]].ok(cli_param)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Failed to convert field {field_name}: {e}"
                )

        @staticmethod
        def model_to_cli_params(
            model_class: type[BaseModel],
        ) -> FlextResult[list[dict[str, Any]]]:
            """Extract all fields from Pydantic model and convert to CLI parameters.

            Args:
                model_class: Pydantic model class to convert

            Returns:
                FlextResult containing list of comprehensive CLI parameter specifications

            """
            try:
                cli_params: list[dict[str, Any]] = []

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

                return FlextResult[list[dict[str, Any]]].ok(cli_params)
            except Exception as e:
                return FlextResult[list[dict[str, Any]]].fail(
                    f"Failed to convert model {model_class.__name__}: {e}"
                )

        @staticmethod
        def model_to_click_options(
            model_class: type[BaseModel],
        ) -> FlextResult[list[dict[str, Any]]]:
            """Generate Click option specifications from Pydantic model.

            Creates complete Click option definitions that can be used to
            programmatically create Click commands with @click.option decorators.

            Args:
                model_class: Pydantic model class to convert

            Returns:
                FlextResult containing list of Click option specifications with:
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
                    return FlextResult[list[dict[str, Any]]].fail(params_result.error)

                click_options: list[dict[str, Any]] = []
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

                return FlextResult[list[dict[str, Any]]].ok(click_options)
            except Exception as e:
                return FlextResult[list[dict[str, Any]]].fail(
                    f"Failed to generate Click options for {model_class.__name__}: {e}"
                )

        @staticmethod
        def cli_args_to_model(
            model_class: type[BaseModel],
            cli_args: dict[str, Any],
        ) -> FlextResult[BaseModel]:
            """Convert CLI arguments dictionary to Pydantic model instance.

            Validates CLI input against model constraints and creates a validated
            model instance. Handles type conversions and validation errors.

            Args:
                model_class: Pydantic model class to instantiate
                cli_args: Dictionary of CLI argument name/value pairs

            Returns:
                FlextResult containing validated model instance

            """
            try:
                # Convert CLI argument names (with dashes) to Python field names (with underscores)
                model_args = {
                    key.replace("-", "_"): value for key, value in cli_args.items()
                }

                # Create and validate model instance
                model_instance = model_class(**model_args)

                return FlextResult[BaseModel].ok(model_instance)
            except Exception as e:
                return FlextResult[BaseModel].fail(
                    f"Failed to create {model_class.__name__} from CLI args: {e}"
                )

        @staticmethod
        def model_to_cli_dict(
            model_instance: BaseModel,
        ) -> FlextResult[dict[str, Any]]:
            """Convert Pydantic model instance to CLI arguments dictionary.

            Useful for converting model instances back to CLI-compatible format
            for display, logging, or passing to other CLI commands.

            Args:
                model_instance: Pydantic model instance

            Returns:
                FlextResult containing dictionary with CLI-style argument names (dashes)

            """
            try:
                # Get model dict
                model_dict = model_instance.model_dump()

                # Convert field names to CLI format (dashes instead of underscores)
                cli_dict = {
                    key.replace("_", "-"): value for key, value in model_dict.items()
                }

                return FlextResult[dict[str, Any]].ok(cli_dict)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Failed to convert model to CLI dict: {e}"
                )

        @staticmethod
        def validate_cli_input(
            model_class: type[BaseModel],
            cli_args: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Validate CLI input against Pydantic model constraints.

            Performs validation without creating a model instance, returning
            validation errors or the validated argument dictionary.

            Args:
                model_class: Pydantic model class for validation
                cli_args: Dictionary of CLI argument name/value pairs

            Returns:
                FlextResult containing validated arguments dict or validation errors

            """
            try:
                # Convert to model to validate
                model_result = FlextCliModels.CliModelConverter.cli_args_to_model(
                    model_class, cli_args
                )

                if model_result.is_failure:
                    return FlextResult[dict[str, Any]].fail(model_result.error)

                # Return validated args
                return FlextResult[dict[str, Any]].ok(cli_args)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"CLI input validation failed: {e}"
                )

        @staticmethod
        def generate_command_spec(
            model_class: type[BaseModel],
            command_name: str,
            command_help: str | None = None,
        ) -> FlextResult[dict[str, Any]]:
            """Generate complete Click command specification from Pydantic model.

            Creates a comprehensive command specification that includes all metadata
            needed to programmatically create a complete Click command with options.

            Args:
                model_class: Pydantic model class defining command parameters
                command_name: Name of the command
                command_help: Help text for the command (defaults to model docstring)

            Returns:
                FlextResult containing complete command specification with:
                - name: Command name
                - help: Command help text
                - options: List of Click option specifications
                - model_class: Reference to the Pydantic model class
                - param_count: Number of parameters
                - required_params: List of required parameter names

            """
            try:
                # Get Click options
                options_result = (
                    FlextCliModels.CliModelConverter.model_to_click_options(model_class)
                )
                if options_result.is_failure:
                    return FlextResult[dict[str, Any]].fail(options_result.error)

                options = options_result.unwrap()

                # Extract required parameters
                required_params = [
                    opt["option_name"] for opt in options if opt["required"]
                ]

                # Use model docstring if no help provided
                if command_help is None:
                    command_help = model_class.__doc__ or f"{command_name} command"

                # Build complete command specification
                command_spec = {
                    "name": command_name,
                    "help": command_help,
                    "options": options,
                    "model_class": model_class,
                    "model_name": model_class.__name__,
                    "param_count": len(options),
                    "required_params": required_params,
                    "optional_params": [
                        opt["option_name"] for opt in options if not opt["required"]
                    ],
                }

                return FlextResult[dict[str, Any]].ok(command_spec)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Failed to generate command spec for {command_name}: {e}"
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
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
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

            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                # Store model metadata on function for CLI builder inspection
                setattr(func, "__cli_model__", model_class)
                setattr(func, "__cli_command_name__", command_name or func.__name__)

                def wrapper(**cli_kwargs: Any) -> Any:
                    # Validate CLI input with Pydantic model
                    validation_result = (
                        FlextCliModels.CliModelConverter.cli_args_to_model(
                            model_class, cli_kwargs
                        )
                    )

                    if validation_result.is_failure:
                        # Return error result
                        return FlextResult[Any].fail(
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
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
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

            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                # Store multiple models metadata
                setattr(func, "__cli_models__", model_classes)
                setattr(func, "__cli_command_name__", command_name or func.__name__)

                def wrapper(**cli_kwargs: Any) -> Any:
                    validated_models: list[BaseModel] = []

                    # Validate with each model
                    for model_class in model_classes:
                        validation_result = (
                            FlextCliModels.CliModelConverter.cli_args_to_model(
                                model_class, cli_kwargs
                            )
                        )

                        if validation_result.is_failure:
                            return FlextResult[Any].fail(
                                f"Validation failed for {model_class.__name__}: {validation_result.error}"
                            )

                        validated_models.append(validation_result.unwrap())

                    # Call with validated models
                    return func(*validated_models)

                return wrapper

            return decorator

    # Base classes for common functionality - using flext-core patterns
    class _BaseEntity(FlextModels.Entity, FlextCliMixins.ValidationMixin):
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
        status: str = Field(default=FlextCliConstants.CommandStatus.PENDING.value)

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

    class _BaseValidatedModel(
        FlextModels.StrictArbitraryTypesModel, FlextCliMixins.ValidationMixin
    ):
        """Base model with common validation patterns."""

        @computed_field
        def model_type(self) -> str:
            """Computed field returning the model type name."""
            return self.__class__.__name__

    class _BaseConfig(_BaseValidatedModel):
        """Base configuration model with common config validation patterns."""

        @model_validator(mode="after")
        def validate_config_consistency(self) -> Self:
            """Validate configuration consistency."""
            # Base validation for all config models
            return self

    class CliCommand(_BaseEntity, FlextCliMixins.BusinessRulesMixin):
        """CLI command model extending _BaseEntity."""

        command_line: str = Field(min_length=1)
        args: FlextTypes.StringList = Field(default_factory=list)
        exit_code: int | None = None
        output: str = Field(default="")
        error_output: str = Field(default="")
        name: str = Field(default="")
        description: str = Field(default="")
        usage: str = Field(default="")
        entry_point: str = Field(default="")
        plugin_version: str = Field(
            default_factory=lambda: FlextCliConstants.CliDefaults.DEFAULT_PROFILE
        )
        # status field inherited from _BaseEntity

        @computed_field
        def command_summary(self) -> FlextTypes.Dict:
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
            sensitive_patterns = ["password", "token", "secret", "key"]
            for pattern in sensitive_patterns:
                if pattern in value.lower():
                    return value.replace(pattern, "*" * len(pattern))
            return value

        @classmethod
        def validate_command_input(
            cls, data: FlextCliTypes.Data.CliCommandData | None
        ) -> FlextResult[FlextCliTypes.Data.CliCommandData | None]:
            """Validate and normalize command input data using railway pattern.

            Args:
                data: Command input data to validate

            Returns:
                FlextResult with validated and normalized data

            """
            # Extract command from data - ensure it's a string
            if not isinstance(data, dict):
                return FlextResult[FlextCliTypes.Data.CliCommandData | None].fail(
                    "Command data must be a dictionary"
                )

            command = data.pop("command")
            if not isinstance(command, str):
                return FlextResult[FlextCliTypes.Data.CliCommandData | None].fail(
                    "Command must be a string"
                )

            # Normalize command data
            normalized_data = {
                "command": command,
                "execution_time": data.get("execution_time"),
                **{k: v for k, v in data.items() if k != "command"},
            }

            return FlextResult[FlextCliTypes.Data.CliCommandData | None].ok(
                normalized_data
            )

        @override
        def __init__(self, **data: object) -> None:
            """Initialize CLI command with Pydantic validation.

            Args:
                **data: Command data including command_line, status, etc.

            """
            # Call parent Pydantic __init__ which handles all field validation
            # Pydantic will automatically convert types as needed
            super().__init__(**data)

        def validate_business_rules(self) -> FlextResult[None]:
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

            return FlextResult[None].ok(None)

        def start_execution(self) -> FlextResult[None]:
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
            return FlextResult[None].ok(None)

        def complete_execution(
            self, exit_code: int, output: str = ""
        ) -> FlextResult[None]:
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
            return FlextResult[None].ok(None)

    class DebugInfo(_BaseValidatedModel):
        """Debug information model extending _BaseValidatedModel."""

        service: str = Field(default="FlextCliDebug")
        status: str = Field(default="operational")
        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        system_info: FlextTypes.StringDict = Field(default_factory=dict)
        config_info: FlextTypes.StringDict = Field(default_factory=dict)
        level: str = Field(default="info")
        message: str = Field(default="")

        @computed_field
        def debug_summary(self) -> FlextTypes.Dict:
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
            self, value: FlextTypes.StringDict, _info: object
        ) -> FlextTypes.StringDict:
            """Serialize system/config info masking sensitive values."""
            sensitive_keys = {"password", "token", "secret", "key", "auth"}
            return {
                k: (
                    "***MASKED***"
                    if any(sens in k.lower() for sens in sensitive_keys)
                    else v
                )
                for k, v in value.items()
            }

        def validate_business_rules(self) -> FlextResult[None]:
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

            return FlextResult[None].ok(None)

    class CliSession(
        FlextModels.Entity,
        FlextCliMixins.BusinessRulesMixin,
    ):
        """CLI session model extending FlextModels.Entity."""

        # id field inherited from FlextModels.Entity
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
        def session_summary(self) -> FlextTypes.Dict:
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
        ) -> list[FlextTypes.Dict]:
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
            domain_events_value: FlextTypes.List = (
                domain_events_obj if isinstance(domain_events_obj, list) else []
            )

            super().__init__(
                id=str(data.get("id", str(uuid.uuid4()))),
                version=version_value,
                created_at=created_at_value,
                updated_at=updated_at_value,
                domain_events=domain_events_value,
            )

            # Set session identifier (auto-generate if not provided)
            if session_id is not None:
                self.session_id = session_id

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate session business rules."""
            # Use mixin validation methods
            session_id_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                "Session ID", self.session_id
            )
            if not session_id_result.is_success:
                return session_id_result

            # Validate user_id if provided
            if self.user_id is not None and not self.user_id.strip():
                return FlextResult[None].fail("User ID cannot be empty")

            valid_statuses = ["active", "completed", "terminated"]
            status_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                "status", self.status, valid_statuses
            )
            if not status_result.is_success:
                return status_result

            return FlextResult[None].ok(None)

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[None]:
            """Add a command to the session.

            Args:
                command: Command to add to the session

            Returns:
                FlextResult[None]: Success if command added, failure otherwise

            """
            try:
                # Add command to the commands list
                self.commands.append(command)

                # Update commands executed count
                self.commands_executed = len(self.commands)

                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to add command to session: {e}")

    # REMOVED: Unused models CliFormatters and CliPipeline
    # These models were not used anywhere in the codebase

    # REMOVED: FlextCliConfig moved to config.py following FLEXT standards
    # Use: from flext_cli.config import FlextCliConfig

    class LoggingConfig(FlextModels.Configuration):
        """Logging configuration model - consolidated from scattered definition.

        This model extends FlextModels.Configuration for logging-specific settings
        while maintaining the consolidated [Project]Models pattern.
        """

        log_level: str = Field(default="INFO", description="Logging level")
        log_format: str = Field(
            default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            description="Log format string",
        )
        console_output: bool = Field(default=True, description="Enable console output")
        log_file: str | None = Field(default=None, description="Log file path")
        log_level_source: str = Field(
            default="default", description="Source of log level"
        )

        @computed_field
        def logging_summary(self) -> FlextTypes.Dict:
            """Computed field for logging configuration summary."""
            return {
                "level": self.log_level,
                "console_enabled": self.console_output,
                "file_logging": self.log_file is not None,
                "format_length": len(self.log_format),
                "source": self.log_level_source,
            }

        @model_validator(mode="after")
        def validate_logging_config(self) -> Self:
            """Validate logging configuration consistency."""
            valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
            if self.log_level not in valid_levels:
                msg = f"Invalid log level: {self.log_level}"
                raise ValueError(msg)
            return self

        @field_serializer("log_file")
        def serialize_log_file(self, value: str | None, _info: object) -> str | None:
            """Serialize log file path with safety checks."""
            if value and "secret" in value.lower():
                return "***SENSITIVE_PATH***"
            return value

    class CliContext(FlextModels.Entity):
        """CLI execution context model extending FlextModels.Entity.

        Manages CLI execution context with enhanced type safety using FlextCliTypes
        instead of generic FlextTypes types. Provides CLI-specific context with domain types
        and uses FlextResult railway pattern for all operations.

        CRITICAL: Moved from context.py to follow FLEXT standards requiring
        ALL models to be declared only in FlextCliModels class.
        """

        def __init__(
            self,
            command: str | None = None,
            arguments: FlextTypes.StringList | None = None,
            environment_variables: FlextCliTypes.Data.CliConfigData | None = None,
            working_directory: str | None = None,
            **data: object,
        ) -> None:
            """Initialize CLI context with enhanced type safety.

            Args:
                command: Command being executed
                arguments: Command line arguments
                environment_variables: Environment variables using CLI-specific config data types
                working_directory: Current working directory
                **data: Additional entity initialization data

            """
            super().__init__(**data)
            self.logger = FlextLogger(__name__)

            # CLI context initialization with domain-specific types
            self._command = command
            self._arguments = arguments or []
            self._environment_variables: FlextCliTypes.Data.CliConfigData = (
                environment_variables or {}
            )
            self._working_directory = working_directory
            self._context_metadata: FlextCliTypes.Data.CliDataDict = {}

            # Context state
            self._is_active = False
            self._created_at = FlextUtilities.Generators.generate_timestamp()

            # Initialize required attributes using constants and config
            self._timeout_seconds = FlextCliConstants.NetworkDefaults.DEFAULT_TIMEOUT
            self._config: FlextCliTypes.Data.CliConfigData = (
                FlextCliConfig().model_dump()
            )

        @property
        def command(self) -> str | None:
            """Get current command being executed."""
            return self._command

        @command.setter
        def command(self, value: str | None) -> None:
            """Set current command being executed."""
            self._command = value

        @property
        def arguments(self) -> FlextTypes.StringList:
            """Get command line arguments."""
            return self._arguments.copy()

        @arguments.setter
        def arguments(self, value: FlextTypes.StringList) -> None:
            """Set command line arguments."""
            self._arguments = value or []

        @property
        def environment_variables(self) -> FlextCliTypes.Data.CliConfigData:
            """Get environment variables using CLI-specific config data types."""
            return self._environment_variables.copy()

        @environment_variables.setter
        def environment_variables(
            self, value: FlextCliTypes.Data.CliConfigData
        ) -> None:
            """Set environment variables using CLI-specific types."""
            self._environment_variables = value or {}

        @property
        def working_directory(self) -> str | None:
            """Get current working directory."""
            return self._working_directory

        @working_directory.setter
        def working_directory(self, value: str | None) -> None:
            """Set current working directory."""
            self._working_directory = value

        @property
        def is_active(self) -> bool:
            """Check if context is currently active."""
            return self._is_active

        def activate(self) -> FlextResult[None]:
            """Activate CLI context for execution."""
            try:
                if self._is_active:
                    return FlextResult[None].fail("Context is already active")

                self._is_active = True
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Context activation failed: {e}")

        def deactivate(self) -> FlextResult[None]:
            """Deactivate CLI context."""
            try:
                if not self._is_active:
                    return FlextResult[None].fail("Context is not currently active")

                self._is_active = False
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Context deactivation failed: {e}")

        def get_environment_variable(self, name: str) -> FlextResult[str]:
            """Get specific environment variable value."""
            if not name or not isinstance(name, str):
                return FlextResult[str].fail("Variable name must be a non-empty string")

            try:
                if name in self._environment_variables:
                    value = self._environment_variables[name]
                    return FlextResult[str].ok(str(value))
                return FlextResult[str].fail(f"Environment variable '{name}' not found")
            except Exception as e:
                return FlextResult[str].fail(
                    f"Environment variable retrieval failed: {e}"
                )

        def set_environment_variable(self, name: str, value: str) -> FlextResult[None]:
            """Set environment variable value."""
            if not name or not isinstance(name, str):
                return FlextResult[None].fail(
                    "Variable name must be a non-empty string"
                )

            if not isinstance(value, str):
                return FlextResult[str].fail("Variable value must be a string")

            try:
                self._environment_variables[name] = value
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(
                    f"Environment variable setting failed: {e}"
                )

        def add_argument(self, argument: str) -> FlextResult[None]:
            """Add command line argument."""
            if not argument or not isinstance(argument, str):
                return FlextResult[None].fail("Argument must be a non-empty string")

            try:
                self._arguments.append(argument)
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Argument addition failed: {e}")

        def remove_argument(self, argument: str) -> FlextResult[None]:
            """Remove command line argument."""
            if not argument or not isinstance(argument, str):
                return FlextResult[None].fail("Argument must be a non-empty string")

            try:
                if argument in self._arguments:
                    self._arguments.remove(argument)
                    return FlextResult[None].ok(None)
                return FlextResult[None].fail(f"Argument '{argument}' not found")
            except Exception as e:
                return FlextResult[None].fail(f"Argument removal failed: {e}")

        def set_metadata(
            self, key: str, value: FlextTypes.JsonValue
        ) -> FlextResult[None]:
            """Set context metadata using CLI-specific data types."""
            if not key or not isinstance(key, str):
                return FlextResult[None].fail("Metadata key must be a non-empty string")

            try:
                self._context_metadata[key] = value
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Metadata setting failed: {e}")

        def get_metadata(self, key: str) -> FlextResult[object]:
            """Get context metadata value."""
            if not key or not isinstance(key, str):
                return FlextResult[object].fail(
                    "Metadata key must be a non-empty string"
                )

            try:
                if key in self._context_metadata:
                    return FlextResult[object].ok(self._context_metadata[key])
                return FlextResult[object].fail(f"Metadata key '{key}' not found")
            except Exception as e:
                return FlextResult[object].fail(f"Metadata retrieval failed: {e}")

        def get_context_summary(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
            """Get comprehensive context summary using CLI-specific data types."""
            try:
                summary: FlextCliTypes.Data.CliDataDict = {
                    "context_id": self.id,
                    "command": self._command or "none",
                    "arguments_count": len(self._arguments),
                    "arguments": list(self._arguments),
                    "environment_variables_count": len(self._environment_variables),
                    "working_directory": self._working_directory or "not_set",
                    "is_active": self._is_active,
                    "created_at": self._created_at,
                    "metadata_keys": list(self._context_metadata.keys()),
                    "metadata_count": len(self._context_metadata),
                }

                return FlextResult[FlextCliTypes.Data.CliDataDict].ok(summary)
            except Exception as e:
                return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                    f"Context summary generation failed: {e}",
                )

        def execute(self) -> FlextResult[FlextTypes.Dict]:
            """Execute the CLI context."""
            try:
                return FlextResult[FlextTypes.Dict].ok({
                    "context_executed": True,
                    "command": self._command,
                    "arguments_count": len(self._arguments) if self._arguments else 0,
                    "timestamp": FlextUtilities.Generators.generate_timestamp(),
                })
            except Exception as e:
                return FlextResult[FlextTypes.Dict].fail(
                    f"Context execution failed: {e}"
                )

        @property
        def timeout_seconds(self) -> int:
            """Get the timeout in seconds."""
            return getattr(self, "_timeout_seconds", 30)

        @timeout_seconds.setter
        def timeout_seconds(self, value: int) -> None:
            """Set the timeout in seconds."""
            self._timeout_seconds = value

        def to_dict(self) -> FlextTypes.Dict:
            """Convert context to dictionary."""
            return {
                "id": self.id,
                "command": self._command,
                "arguments": self._arguments or [],
                "environment_variables": self._environment_variables or {},
                "working_directory": self._working_directory,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "timeout_seconds": self.timeout_seconds,
            }

    # REMOVED: PipelineConfig, AdvancedServicePattern, ServiceOrchestrator,
    # CentralizedValidation, and AdvancedServiceOrchestrator classes.
    # These were over-engineered patterns not used anywhere in the codebase.
    # Total removed: ~1,016 lines of unused code


__all__ = [
    "FlextCliModels",
]
