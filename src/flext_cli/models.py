"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

EXPECTED MYPY ISSUES (documented for awareness):
- None currently (CliContext moved to context.py following flext-core patterns)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import typing
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, Self, cast, get_args, get_origin

from flext_core import (
    FlextConstants,
    FlextLogger,
    FlextModels,
    FlextResult,
    FlextTypes,
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
from pydantic.functional_validators import BeforeValidator
from pydantic_core import PydanticUndefined

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes

logger = FlextLogger(__name__)


# =============================================================================
# MODULE-LEVEL VALIDATORS (Pydantic 2.11+ BeforeValidator pattern)
# =============================================================================


def _validate_log_level(v: str) -> str:
    """Validate log level using flext-core constants (no duplication).

    Args:
        v: Log level string to validate

    Returns:
        Normalized log level (uppercase)

    Raises:
        ValueError: If log level not in valid levels

    """
    valid_levels = set(FlextConstants.Logging.VALID_LEVELS)
    level_upper = v.upper()
    if level_upper not in valid_levels:
        msg = f"Invalid log level: {v}. Must be one of {valid_levels}"
        raise ValueError(msg)
    return level_upper


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
    name: str = Field(
        default=FlextCliConstants.PROJECT_NAME,
        description=FlextCliConstants.FieldDescriptions.PROJECT_NAME,
    )

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
            "title": FlextCliConstants.ModelsJsonSchema.TITLE,
            "description": FlextCliConstants.ModelsJsonSchema.DESCRIPTION,
            "examples": [
                {
                    "cli_command": {
                        "command_line": FlextCliConstants.ModelsJsonSchema.EXAMPLE_COMMAND,
                        FlextCliConstants.ModelsFieldNames.STATUS: FlextCliConstants.CommandStatus.PENDING.value,
                        "args": [FlextCliConstants.ModelsJsonSchema.EXAMPLE_ARGS],
                    }
                }
            ],
        },
    )

    @field_serializer("model_summary")
    def serialize_model_summary(
        self, value: dict[str, str], _info: typing.Any
    ) -> dict[str, str | dict[str, str | int]]:
        """Serialize model summary with additional metadata."""
        return {
            **value,
            "_metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "total_models": len(value),
                "serialization_version": FlextCliConstants.ModelsDefaults.SERIALIZATION_VERSION,
            },
        }

    def execute(self) -> FlextResult[object]:
        """Execute model operations - placeholder for testing."""
        return FlextResult[object].ok(None)

    # ========================================================================
    # DICT REPLACEMENT MODELS - Define before usage
    # ========================================================================

    class CliParameterSpec(FlextModels.StrictArbitraryTypesModel):
        """CLI parameter specification model - replaces dict in CLI parameter handling.

        Provides structured validation for CLI parameter specifications used in
        model-to-CLI conversion utilities.
        """

        name: str = Field(
            description=FlextCliConstants.CliParameterSpecDescriptions.NAME
        )
        field_name: str = Field(
            description=FlextCliConstants.CliParameterSpecDescriptions.FIELD_NAME
        )
        param_type: type = Field(
            description=FlextCliConstants.CliParameterSpecDescriptions.PARAM_TYPE
        )
        click_type: str = Field(
            description=FlextCliConstants.CliParameterSpecDescriptions.CLICK_TYPE
        )
        required: bool = Field(
            description=FlextCliConstants.CliParameterSpecDescriptions.REQUIRED
        )
        default: FlextTypes.JsonValue | None = Field(
            default=None,
            description=FlextCliConstants.CliParameterSpecDescriptions.DEFAULT,
        )
        help: str = Field(
            description=FlextCliConstants.CliParameterSpecDescriptions.HELP
        )
        validators: list[Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]] = (
            Field(
                default_factory=list,
                description=FlextCliConstants.CliParameterSpecDescriptions.VALIDATORS,
            )
        )
        metadata: dict[str, FlextTypes.JsonValue] = Field(
            default_factory=dict,
            description=FlextCliConstants.CliParameterSpecDescriptions.METADATA,
        )

    class CliOptionSpec(FlextModels.StrictArbitraryTypesModel):
        """Click option specification model - replaces dict[str, object] in Click option generation.

        Provides structured validation for Click option specifications generated
        from Pydantic model fields.
        """

        option_name: str = Field(
            description=FlextCliConstants.CliOptionSpecDescriptions.OPTION_NAME
        )
        param_decls: list[str] = Field(
            description=FlextCliConstants.CliOptionSpecDescriptions.PARAM_DECLS
        )
        type: str = Field(description=FlextCliConstants.CliOptionSpecDescriptions.TYPE)
        default: FlextTypes.JsonValue | None = Field(
            default=None,
            description=FlextCliConstants.CliOptionSpecDescriptions.DEFAULT,
        )
        help: str = Field(description=FlextCliConstants.CliOptionSpecDescriptions.HELP)
        required: bool = Field(
            description=FlextCliConstants.CliOptionSpecDescriptions.REQUIRED
        )
        show_default: bool = Field(
            description=FlextCliConstants.CliOptionSpecDescriptions.SHOW_DEFAULT
        )
        metadata: dict[str, FlextTypes.JsonValue] = Field(
            default_factory=dict,
            description=FlextCliConstants.CliOptionSpecDescriptions.METADATA,
        )

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
                str: FlextCliConstants.ClickTypes.STRING,
                int: FlextCliConstants.ClickTypes.INT,
                float: FlextCliConstants.ClickTypes.FLOAT,
                bool: FlextCliConstants.ClickTypes.BOOL,
                list: FlextCliConstants.ClickTypes.STRING,
                dict: FlextCliConstants.ClickTypes.STRING,
            }
            return type_map.get(python_type, FlextCliConstants.ClickTypes.STRING)

        @staticmethod
        def field_to_cli_param(
            field_name: str, field_info: fields.FieldInfo
        ) -> FlextResult[FlextCliModels.CliParameterSpec]:
            """Convert Pydantic Field to comprehensive CLI parameter specification.

            Args:
                field_name: Name of the field
                field_info: Pydantic FieldInfo object

            Returns:
                FlextResult containing CLI parameter specification dict[str, object] with:
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
                    return FlextResult[FlextCliModels.CliParameterSpec].fail(
                        FlextCliConstants.ModelsErrorMessages.FIELD_NO_TYPE_ANNOTATION.format(
                            field_name=field_name
                        )
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
                description = (
                    field_info.description
                    or FlextCliConstants.ModelsDefaults.DEFAULT_FIELD_DESCRIPTION.format(
                        field_name=field_name
                    )
                )

                # Extract validation constraints from metadata
                validators: list[
                    Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]
                ] = []
                metadata: dict[str, FlextTypes.JsonValue] = {}

                if hasattr(field_info, "metadata"):
                    for meta_item in field_info.metadata:
                        if hasattr(meta_item, "__dict__"):
                            metadata.update(meta_item.__dict__)

                # Build comprehensive CLI parameter spec
                cli_param = FlextCliModels.CliParameterSpec(
                    name=field_name.replace(
                        FlextCliConstants.CliParamDefaults.FIELD_NAME_SEPARATOR,
                        FlextCliConstants.CliParamDefaults.PARAM_NAME_SEPARATOR,
                    ),
                    field_name=field_name,
                    param_type=python_type,
                    click_type=click_type,
                    required=is_required,
                    default=default_value,
                    help=description,
                    validators=validators,
                    metadata=metadata,
                )

                return FlextResult[FlextCliModels.CliParameterSpec].ok(cli_param)
            except Exception as e:
                return FlextResult[FlextCliModels.CliParameterSpec].fail(
                    FlextCliConstants.ModelsErrorMessages.FAILED_FIELD_CONVERSION.format(
                        field_name=field_name, error=str(e)
                    )
                )

        @staticmethod
        def model_to_cli_params(
            model_class: type[BaseModel],
        ) -> FlextResult[list[FlextCliModels.CliParameterSpec]]:
            """Extract all fields from Pydantic model and convert to CLI parameters.

            Args:
                model_class: Pydantic model class to convert

            Returns:
                FlextResult containing list of comprehensive CLI parameter specifications

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

                return FlextResult[list[FlextCliModels.CliParameterSpec]].ok(cli_params)
            except Exception as e:
                return FlextResult[list[FlextCliModels.CliParameterSpec]].fail(
                    FlextCliConstants.ModelsErrorMessages.FAILED_MODEL_CONVERSION.format(
                        model_name=model_class.__name__, error=str(e)
                    )
                )

        @staticmethod
        def model_to_click_options(
            model_class: type[BaseModel],
        ) -> FlextResult[list[FlextCliModels.CliOptionSpec]]:
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
                    return FlextResult[list[FlextCliModels.CliOptionSpec]].fail(
                        params_result.error
                    )

                click_options: list[FlextCliModels.CliOptionSpec] = []
                for param in params_result.unwrap():
                    option_name = f"{FlextCliConstants.CliParamDefaults.OPTION_PREFIX}{param.name}"

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

                return FlextResult[list[FlextCliModels.CliOptionSpec]].ok(click_options)
            except Exception as e:
                return FlextResult[list[FlextCliModels.CliOptionSpec]].fail(
                    FlextCliConstants.ModelsErrorMessages.FAILED_CLICK_OPTIONS_GENERATION.format(
                        model_name=model_class.__name__, error=str(e)
                    )
                )

        @staticmethod
        def cli_args_to_model(
            model_class: type[BaseModel],
            cli_args: dict[str, object],
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
                    key.replace(
                        FlextCliConstants.CliParamDefaults.PARAM_NAME_SEPARATOR,
                        FlextCliConstants.CliParamDefaults.FIELD_NAME_SEPARATOR,
                    ): value
                    for key, value in cli_args.items()
                }

                # Create and validate model instance
                model_instance = model_class(**model_args)

                return FlextResult[BaseModel].ok(model_instance)
            except Exception as e:
                return FlextResult[BaseModel].fail(
                    FlextCliConstants.ModelsErrorMessages.FAILED_MODEL_CREATION_FROM_CLI.format(
                        model_name=model_class.__name__, error=str(e)
                    )
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
        ) -> Callable[
            [Callable[[BaseModel], FlextTypes.JsonValue | FlextResult[object]]],
            Callable[..., FlextTypes.JsonValue | FlextResult[object]],
        ]:
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

            def decorator(
                func: Callable[[BaseModel], FlextTypes.JsonValue | FlextResult[object]],
            ) -> Callable[..., FlextTypes.JsonValue | FlextResult[object]]:
                # Store model metadata on function for CLI builder inspection
                setattr(
                    func,
                    FlextCliConstants.CliParamDefaults.MAGIC_ATTR_CLI_MODEL,
                    model_class,
                )
                setattr(
                    func,
                    FlextCliConstants.CliParamDefaults.MAGIC_ATTR_CLI_COMMAND_NAME,
                    command_name or func.__name__,
                )

                def wrapper(
                    **cli_kwargs: FlextTypes.JsonValue,
                ) -> FlextTypes.JsonValue | FlextResult[object]:
                    # Validate CLI input with Pydantic model
                    from typing import cast

                    validation_result = (
                        FlextCliModels.CliModelConverter.cli_args_to_model(
                            model_class, cast("dict[str, object]", cli_kwargs)
                        )
                    )

                    if validation_result.is_failure:
                        # Return error result
                        return FlextResult[object].fail(
                            FlextCliConstants.ModelsErrorMessages.INVALID_INPUT.format(
                                error=validation_result.error
                            )
                        )

                    validated_model = validation_result.unwrap()

                    # Call original function with validated model
                    return func(validated_model)

                return wrapper

            return decorator

        @staticmethod
        def cli_from_multiple_models(
            *model_classes: type[BaseModel], command_name: str | None = None
        ) -> Callable[
            [Callable[..., FlextTypes.JsonValue | FlextResult[object]]],
            Callable[..., FlextTypes.JsonValue | FlextResult[object]],
        ]:
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

            def decorator(
                func: Callable[..., FlextTypes.JsonValue | FlextResult[object]],
            ) -> Callable[..., FlextTypes.JsonValue | FlextResult[object]]:
                # Store multiple models metadata
                setattr(
                    func,
                    FlextCliConstants.CliParamDefaults.MAGIC_ATTR_CLI_MODELS,
                    model_classes,
                )
                setattr(
                    func,
                    FlextCliConstants.CliParamDefaults.MAGIC_ATTR_CLI_COMMAND_NAME,
                    command_name or func.__name__,
                )

                def wrapper(
                    **cli_kwargs: FlextTypes.JsonValue,
                ) -> FlextTypes.JsonValue | FlextResult[object]:
                    validated_models: list[BaseModel] = []

                    # Validate with each model
                    for model_class in model_classes:
                        from typing import cast

                        validation_result = (
                            FlextCliModels.CliModelConverter.cli_args_to_model(
                                model_class, cast("dict[str, object]", cli_kwargs)
                            )
                        )

                        if validation_result.is_failure:
                            return FlextResult[object].fail(
                                FlextCliConstants.ModelsErrorMessages.VALIDATION_FAILED_FOR_MODEL.format(
                                    model_name=model_class.__name__,
                                    error=validation_result.error,
                                )
                            )

                        validated_models.append(validation_result.unwrap())

                    # Call with validated models
                    return func(*validated_models)

                return wrapper

            return decorator

    # =========================================================================
    # CLI DOMAIN MODELS - Using FlextModels base classes directly
    # =========================================================================

    class CliCommand(FlextModels.Entity, FlextCliMixins.BusinessRulesMixin):
        """CLI command model with comprehensive CLI execution tracking.

        Extends FlextModels.Entity (provides id, created_at, updated_at, version, domain_events).
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
            description=FlextCliConstants.CliCommandDescriptions.COMMAND_LINE,
            examples=["flext validate", "flext deploy --env production"],
        )
        args: list[str] = Field(
            default_factory=list,
            description=FlextCliConstants.CliCommandDescriptions.ARGS,
            examples=[["validate"], ["deploy", "--env", "production"]],
        )
        status: str = Field(
            default=FlextCliConstants.CommandStatus.PENDING.value,
            description=FlextCliConstants.CliCommandDescriptions.STATUS,
            examples=[
                FlextCliConstants.CommandStatus.PENDING.value,
                FlextCliConstants.CommandStatus.RUNNING.value,
                FlextCliConstants.CommandStatus.COMPLETED.value,
                FlextCliConstants.CommandStatus.FAILED.value,
            ],
        )
        exit_code: int | None = Field(
            default=None,
            description=FlextCliConstants.CliCommandDescriptions.EXIT_CODE,
            examples=[0, 1, 127],
        )
        output: str = Field(
            default=FlextCliConstants.CliCommandDefaults.DEFAULT_OUTPUT,
            description=FlextCliConstants.CliCommandDescriptions.OUTPUT,
        )
        error_output: str = Field(
            default=FlextCliConstants.CliCommandDefaults.DEFAULT_ERROR_OUTPUT,
            description=FlextCliConstants.CliCommandDescriptions.ERROR_OUTPUT,
        )
        execution_time: float | None = Field(
            default=None,
            ge=0.0,
            description=FlextCliConstants.CliCommandDescriptions.EXECUTION_TIME,
            examples=[0.123, 5.678, 120.5],
        )
        result: FlextCliTypes.Data.CliDataDict | None = Field(
            default=None,
            description=FlextCliConstants.CliCommandDescriptions.RESULT,
        )
        kwargs: FlextCliTypes.Data.CliDataDict = Field(
            default_factory=dict,
            description=FlextCliConstants.CliCommandDescriptions.KWARGS,
        )
        name: str = Field(
            default=FlextCliConstants.ModelsDefaults.EMPTY_STRING,
            description=FlextCliConstants.CliCommandDescriptions.NAME,
            examples=["validate", "deploy", "test"],
        )
        description: str = Field(
            default=FlextCliConstants.ModelsDefaults.EMPTY_STRING,
            description=FlextCliConstants.CliCommandDescriptions.DESCRIPTION,
        )
        usage: str = Field(
            default=FlextCliConstants.ModelsDefaults.EMPTY_STRING,
            description=FlextCliConstants.CliCommandDescriptions.USAGE,
        )
        entry_point: str = Field(
            default=FlextCliConstants.ModelsDefaults.EMPTY_STRING,
            description=FlextCliConstants.CliCommandDescriptions.ENTRY_POINT,
        )
        plugin_version: str = Field(
            default=FlextCliConstants.DEFAULT,
            description=FlextCliConstants.CliCommandDescriptions.PLUGIN_VERSION,
        )

        # Pydantic 2.11 computed fields for derived properties
        @computed_field
        def is_completed(self) -> bool:
            """Check if command execution is completed."""
            return self.status == FlextCliConstants.CommandStatus.COMPLETED.value

        @computed_field
        def is_failed(self) -> bool:
            """Check if command execution failed."""
            return self.status == FlextCliConstants.CommandStatus.FAILED.value

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
                raise ValueError(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_WITH_EXIT_CODE_PENDING
                )

            # If command has output, it should have been executed
            if (
                self.output
                and self.status == FlextCliConstants.CommandStatus.PENDING.value
            ):
                raise ValueError(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_WITH_OUTPUT_PENDING
                )

            return self

        @field_serializer("command_line")
        def serialize_command_line(self, value: str, _info: typing.Any) -> str:
            """Serialize command line with safety checks for sensitive commands."""
            # Mask potentially sensitive command parts
            sensitive_patterns = [
                FlextCliConstants.DictKeys.PASSWORD,
                FlextCliConstants.DictKeys.TOKEN,
                FlextCliConstants.DictKeys.SECRET,
                FlextCliConstants.DictKeys.KEY,
            ]
            for pattern in sensitive_patterns:
                if pattern in value.lower():
                    return value.replace(
                        pattern,
                        FlextCliConstants.CliParamDefaults.MASK_CHAR * len(pattern),
                    )
            return value

        @classmethod
        def validate_command_input(
            cls, data: object
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
                    FlextCliConstants.ModelsErrorMessages.COMMAND_DATA_MUST_BE_DICT
                )

            if "command" not in data:
                return FlextResult[FlextCliTypes.Data.CliCommandData | None].fail(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_FIELD_REQUIRED
                )

            command = data.pop("command")
            if not isinstance(command, str):
                return FlextResult[FlextCliTypes.Data.CliCommandData | None].fail(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_MUST_BE_STRING
                )

            # Normalize command data
            normalized_data: FlextCliTypes.Data.CliDataDict = {
                "command": command,
                "execution_time": data.get("execution_time"),
                **{k: v for k, v in data.items() if k != "command"},
            }

            # Return normalized data (type is already correct)
            return FlextResult[FlextCliTypes.Data.CliCommandData | None].ok(
                normalized_data
            )

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

    class CliSession(
        FlextModels.Entity,
        FlextCliMixins.BusinessRulesMixin,
    ):
        """CLI session model with comprehensive session tracking.

        Extends FlextModels.Entity (provides id, created_at, updated_at, version, domain_events).
        Tracks CLI session lifecycle, command execution history, and user activity.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        - model_validator for cross-field validation
        """

        # Session-specific fields (id, created_at, updated_at inherited from Entity)
        session_id: str = Field(
            default_factory=lambda: f"{FlextCliConstants.CliSessionDefaults.SESSION_ID_PREFIX}{datetime.now(UTC).strftime(FlextCliConstants.CliSessionDefaults.DATETIME_FORMAT)}",
            description=FlextCliConstants.CliSessionDescriptions.SESSION_ID,
            examples=["session_20250113_143022_123456"],
        )

        start_time: str | None = Field(
            default=None,
            description=FlextCliConstants.CliSessionDescriptions.START_TIME,
            examples=["2025-01-13T14:30:22Z"],
        )

        end_time: str | None = Field(
            default=None,
            description=FlextCliConstants.CliSessionDescriptions.END_TIME,
            examples=["2025-01-13T15:45:30Z"],
        )
        last_activity: str | None = Field(
            default=None,
            description=FlextCliConstants.CliSessionDescriptions.LAST_ACTIVITY,
            examples=["2025-01-13T15:30:00Z"],
        )
        internal_duration_seconds: float = Field(
            default=FlextCliConstants.ModelsDefaults.ZERO_FLOAT,
            ge=0.0,
            description=FlextCliConstants.CliSessionDescriptions.INTERNAL_DURATION,
        )
        commands_executed: int = Field(
            default=FlextCliConstants.ModelsDefaults.ZERO_INT,
            ge=0,
            description=FlextCliConstants.CliSessionDescriptions.COMMANDS_EXECUTED,
        )
        commands: list[FlextCliModels.CliCommand] = Field(
            default_factory=list,
            description=FlextCliConstants.CliSessionDescriptions.COMMANDS,
        )
        status: str = Field(
            default=FlextCliConstants.SessionStatus.ACTIVE.value,
            description=FlextCliConstants.CliSessionDescriptions.STATUS,
            examples=[
                FlextCliConstants.SessionStatus.ACTIVE.value,
                FlextCliConstants.SessionStatus.COMPLETED.value,
                FlextCliConstants.SessionStatus.TERMINATED.value,
            ],
        )
        user_id: str | None = Field(
            default=None,
            description=FlextCliConstants.CliSessionDescriptions.USER_ID,
        )

        # Pydantic 2.11 computed fields
        @computed_field
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
            return self.status == FlextCliConstants.SessionStatus.ACTIVE.value

        @computed_field
        def session_summary(self) -> FlextCliModels.CliSessionData:
            """Computed field for session activity summary."""
            # Compute duration the same way as the computed field
            duration = self.internal_duration_seconds
            if self.start_time and self.end_time:
                try:
                    start = datetime.fromisoformat(self.start_time)
                    end = datetime.fromisoformat(self.end_time)
                    duration = (end - start).total_seconds()
                except (ValueError, AttributeError):
                    pass

            return FlextCliModels.CliSessionData(
                session_id=self.session_id,
                is_active=self.status == FlextCliConstants.SessionStatus.ACTIVE.value,
                commands_count=len(self.commands),
                duration_minutes=round(
                    duration / FlextCliConstants.CliSessionDefaults.SECONDS_PER_MINUTE,
                    2,
                ),
                has_user=self.user_id is not None,
                last_activity_age=self._calculate_activity_age(),
            )

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
            if self.internal_duration_seconds < 0:
                raise ValueError(
                    FlextCliConstants.ModelsErrorMessages.DURATION_CANNOT_BE_NEGATIVE
                )

            return self

        @field_serializer("commands")
        def serialize_commands(
            self, value: list[FlextCliModels.CliCommand], _info: typing.Any
        ) -> list[dict[str, object]]:
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate session business rules."""
            # Use mixin validation methods
            session_id_result = FlextCliMixins.ValidationMixin.validate_not_empty(
                FlextCliConstants.ModelsFieldNames.SESSION_ID, self.session_id
            )
            if not session_id_result.is_success:
                return session_id_result

            # Validate user_id if provided
            if self.user_id is not None and not self.user_id.strip():
                return FlextResult[None].fail(
                    FlextCliConstants.ModelsErrorMessages.USER_ID_EMPTY
                )

            valid_statuses = FlextCliConstants.SESSION_STATUSES_LIST
            status_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                FlextCliConstants.ModelsFieldNames.STATUS, self.status, valid_statuses
            )
            if not status_result.is_success:
                return status_result

            return FlextResult[None].ok(None)

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[None]:
            """Add a command to the session."""
            if command in self.commands:
                return FlextResult[None].fail(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_ALREADY_EXISTS
                )

            self.commands.append(command)
            self.commands_executed = len(self.commands)
            return FlextResult[None].ok(None)

    class DebugInfo(
        FlextModels.StrictArbitraryTypesModel, FlextCliMixins.ValidationMixin
    ):
        """Debug information model with comprehensive diagnostic data.

        Extends FlextModels.StrictArbitraryTypesModel for strict validation.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        - field_serializer for sensitive data masking
        """

        service: str = Field(
            default=FlextCliConstants.DebugServiceNames.DEBUG,
            description=FlextCliConstants.DebugInfoDescriptions.SERVICE,
            examples=["FlextCliDebug", "FlextCliCore", "FlextCliCommands"],
        )
        status: str = Field(
            default=FlextCliConstants.ServiceStatus.OPERATIONAL.value,
            description=FlextCliConstants.DebugInfoDescriptions.STATUS,
            examples=[
                FlextCliConstants.ServiceStatus.OPERATIONAL.value,
                FlextCliConstants.ServiceStatus.DEGRADED.value,
                FlextCliConstants.ServiceStatus.ERROR.value,
            ],
        )
        timestamp: datetime = Field(
            default_factory=lambda: datetime.now(UTC),
            description=FlextCliConstants.DebugInfoDescriptions.TIMESTAMP,
        )
        system_info: dict[str, str] = Field(
            default_factory=dict,
            description=FlextCliConstants.DebugInfoDescriptions.SYSTEM_INFO,
        )
        config_info: dict[str, str] = Field(
            default_factory=dict,
            description=FlextCliConstants.DebugInfoDescriptions.CONFIG_INFO,
        )
        level: str = Field(
            default=FlextConstants.Logging.INFO,
            description=FlextCliConstants.DebugInfoDescriptions.LEVEL,
            examples=[
                FlextConstants.Logging.DEBUG,
                FlextConstants.Logging.INFO,
                FlextConstants.Logging.WARNING,
                FlextConstants.Logging.ERROR,
                FlextConstants.Logging.CRITICAL,
            ],
        )
        message: str = Field(
            default=FlextCliConstants.ModelsDefaults.EMPTY_STRING,
            description=FlextCliConstants.DebugInfoDescriptions.MESSAGE,
        )

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
            # Level-specific validation using FlextModels.Validation
            if (
                self.level in FlextCliConstants.CRITICAL_DEBUG_LEVELS_SET
                and not self.message
            ):
                raise ValueError(
                    FlextCliConstants.ModelsErrorMessages.CRITICAL_DEBUG_REQUIRES_MESSAGE.format(
                        level=self.level
                    )
                )
            return self

        @field_serializer("system_info", "config_info")
        def serialize_sensitive_info(
            self, value: dict[str, str], _info: typing.Any
        ) -> dict[str, str]:
            """Serialize system/config info masking sensitive values."""
            sensitive_keys = {
                FlextCliConstants.DictKeys.PASSWORD,
                FlextCliConstants.DictKeys.TOKEN,
                FlextCliConstants.DictKeys.SECRET,
                FlextCliConstants.DictKeys.KEY,
                FlextCliConstants.DictKeys.AUTH,
            }
            return {
                k: (
                    FlextCliConstants.CliParamDefaults.MASKED_SENSITIVE
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
            valid_levels = FlextCliConstants.DEBUG_LEVELS_LIST
            level_result = FlextCliMixins.ValidationMixin.validate_enum_value(
                "level", self.level, valid_levels
            )
            if not level_result.is_success:
                return level_result

            return FlextResult[None].ok(None)

    class LoggingConfig(
        FlextModels.ArbitraryTypesModel, FlextCliMixins.ValidationMixin
    ):
        """Logging configuration model for CLI operations.

        Extends FlextModels.ArbitraryTypesModel for flexible configuration.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        """

        log_level: Annotated[str, BeforeValidator(_validate_log_level)] = Field(
            ...,
            description=FlextCliConstants.LoggingConfigDescriptions.LOG_LEVEL,
            examples=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        log_format: str = Field(
            ...,
            description=FlextCliConstants.LoggingConfigDescriptions.LOG_FORMAT,
            examples=["%(levelname)s: %(message)s", "json", "plain"],
        )
        console_output: bool = Field(
            default=FlextCliConstants.ModelsDefaults.FALSE_BOOL,
            description=FlextCliConstants.LoggingConfigDescriptions.CONSOLE_OUTPUT,
        )
        log_file: str | None = Field(
            default=None,
            description=FlextCliConstants.LoggingConfigDescriptions.LOG_FILE,
            examples=["/var/log/flext-cli.log", "~/.flext/cli.log"],
        )

        # Pydantic 2.11 computed fields
        @computed_field
        def has_file_output(self) -> bool:
            """Check if file logging is enabled."""
            return self.log_file is not None and len(self.log_file) > 0

        @computed_field
        def logging_summary(self) -> FlextCliModels.CliLoggingData:
            """Comprehensive logging configuration summary."""
            return FlextCliModels.CliLoggingData(
                level=self.log_level,
                format=self.log_format,
                console_output=self.console_output,
                log_file=self.log_file,
                has_file_output=self.log_file is not None and len(self.log_file) > 0,
            )

    # NOTE: CliConfig has been moved to config.py as FlextCliConfig
    # Import from flext_cli.config instead of using this duplicate

    # ========================================================================
    # ADDITIONAL DICT REPLACEMENT MODELS
    # ========================================================================

    class CliCommandResult(FlextModels.StrictArbitraryTypesModel):
        """CLI command result model - replaces dict[str, object] in command execution results.

        Provides structured validation for command execution results and metadata.
        """

        id: str = Field(description=FlextCliConstants.CliCommandResultDescriptions.ID)
        command_line: str = Field(
            description=FlextCliConstants.CliCommandResultDescriptions.COMMAND_LINE
        )
        status: str = Field(
            description=FlextCliConstants.CliCommandResultDescriptions.STATUS
        )
        exit_code: int | None = Field(
            default=None,
            description=FlextCliConstants.CliCommandResultDescriptions.EXIT_CODE,
        )
        created_at: str = Field(
            description=FlextCliConstants.CliCommandResultDescriptions.CREATED_AT
        )
        execution_time: float | None = Field(
            default=None,
            description=FlextCliConstants.CliCommandResultDescriptions.EXECUTION_TIME,
        )

    class CliDebugData(FlextModels.StrictArbitraryTypesModel):
        """CLI debug data model - replaces dict[str, object] in debug information.

        Provides structured validation for debug information and diagnostic data.
        """

        service: str = Field(
            description=FlextCliConstants.CliDebugDataDescriptions.SERVICE
        )
        level: str = Field(description=FlextCliConstants.CliDebugDataDescriptions.LEVEL)
        status: str = Field(
            description=FlextCliConstants.CliDebugDataDescriptions.STATUS
        )
        has_system_info: bool = Field(
            description=FlextCliConstants.CliDebugDataDescriptions.HAS_SYSTEM_INFO
        )
        has_config_info: bool = Field(
            description=FlextCliConstants.CliDebugDataDescriptions.HAS_CONFIG_INFO
        )
        total_stats: int = Field(
            description=FlextCliConstants.CliDebugDataDescriptions.TOTAL_STATS
        )
        message_length: int = Field(
            description=FlextCliConstants.CliDebugDataDescriptions.MESSAGE_LENGTH
        )
        age_seconds: float = Field(
            description=FlextCliConstants.CliDebugDataDescriptions.AGE_SECONDS
        )

    class CliSessionData(FlextModels.StrictArbitraryTypesModel):
        """CLI session data model - replaces dict[str, object] in session summaries.

        Provides structured validation for session summary information.
        """

        session_id: str = Field(
            description=FlextCliConstants.CliSessionDataDescriptions.SESSION_ID
        )
        is_active: bool = Field(
            description=FlextCliConstants.CliSessionDataDescriptions.IS_ACTIVE
        )
        commands_count: int = Field(
            description=FlextCliConstants.CliSessionDataDescriptions.COMMANDS_COUNT
        )
        duration_minutes: float = Field(
            description=FlextCliConstants.CliSessionDataDescriptions.DURATION_MINUTES
        )
        has_user: bool = Field(
            description=FlextCliConstants.CliSessionDataDescriptions.HAS_USER
        )
        last_activity_age: float | None = Field(
            default=None,
            description=FlextCliConstants.CliSessionDataDescriptions.LAST_ACTIVITY_AGE,
        )

    class CliLoggingData(FlextModels.ArbitraryTypesModel):
        """CLI logging data model - replaces dict[str, object] in logging summaries.

        Provides structured validation for logging configuration summaries.
        """

        level: str = Field(
            description=FlextCliConstants.CliLoggingDataDescriptions.LEVEL
        )
        format: str = Field(
            description=FlextCliConstants.CliLoggingDataDescriptions.FORMAT
        )
        console_output: bool = Field(
            description=FlextCliConstants.CliLoggingDataDescriptions.CONSOLE_OUTPUT
        )
        log_file: str | None = Field(
            default=None,
            description=FlextCliConstants.CliLoggingDataDescriptions.LOG_FILE,
        )
        has_file_output: bool = Field(
            description=FlextCliConstants.CliLoggingDataDescriptions.HAS_FILE_OUTPUT
        )


__all__ = [
    "FlextCliModels",
]
