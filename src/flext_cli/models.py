"""FLEXT CLI Models - Single unified class following FLEXT standards.

Provides CLI-specific Pydantic models using flext-core standardization.
Single FlextCliModels class with nested model subclasses following FLEXT pattern.

EXPECTED MYPY ISSUES (documented for awareness):
- None currently (CliContext moved to context.py following flext-core patterns)

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import functools
import inspect
import types
import typing
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, Self, get_args, get_origin, get_type_hints

import typer
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
    StringConstraints,
    computed_field,
    field_serializer,
    field_validator,
    fields,
    model_validator,
)
from pydantic_core import PydanticUndefined
from typer.models import OptionInfo

from flext_cli._models_config import ConfigServiceExecutionResult
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities

logger = FlextLogger(__name__)

# Type alias for intermediate field metadata dictionaries
# Contains Python types (type) which are not JsonValue
type FieldMetadataDict = dict[
    str,
    type
    | str
    | bool
    | FlextTypes.JsonValue
    | list[Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]]
    | dict[str, FlextTypes.JsonValue]
    | None,
]

# Type alias for field validation result tuple
type FieldValidationResult = tuple[
    type,
    str,
    bool,
    str,
    list[Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]],
    dict[str, FlextTypes.JsonValue],
]


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
                        "command_line": (
                            FlextCliConstants.ModelsJsonSchema.EXAMPLE_COMMAND
                        ),
                        FlextCliConstants.ModelsFieldNames.STATUS: (
                            FlextCliConstants.CommandStatus.PENDING.value
                        ),
                        "args": [FlextCliConstants.ModelsJsonSchema.EXAMPLE_ARGS],
                    }
                }
            ],
        },
    )

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:
        """Execute model operations - returns success result.

        Returns:
            FlextResult[FlextTypes.JsonDict]: Service execution result

        """
        return FlextResult[FlextTypes.JsonDict].ok({})

    # ========================================================================
    # VALIDATION HELPERS - Delegated to FlextCliUtilities.CliValidation
    # ========================================================================
    # All validation helpers moved to utilities.py following DRY principle
    # Use FlextCliUtilities.CliValidation.validate_field_not_empty()
    # Use FlextCliUtilities.CliValidation.validate_field_in_list()

    # ========================================================================
    # DICT REPLACEMENT MODELS - Define before usage
    # ========================================================================

    class CliParameterSpec(FlextModels.ArbitraryTypesModel):
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

    class CliOptionSpec(FlextModels.ArbitraryTypesModel):
        """Click option specification model.

        Replaces FlextTypes.JsonDict in Click option generation.

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
            command_spec = CliModelConverter.generate_command_spec(
                MyModel, "my-command"
            )
        """

        @staticmethod
        def convert_field_to_cli_param(
            field_name: str,
            field_info: fields.FieldInfo,
        ) -> FlextResult[FlextCliModels.CliParameterSpec]:
            """Convert Pydantic field to CLI parameter specification.

            Railway pattern: validate → convert types → extract properties → build spec

            Args:
                field_name: Field name
                field_info: Pydantic FieldInfo

            Returns:
                FlextResult containing CLI parameter specification

            """
            converter = FlextCliModels.CliModelConverter
            return (
                converter.validate_field_type(field_name, field_info)
                .flat_map(converter.convert_field_types)
                .flat_map(
                    lambda types: converter.extract_field_properties(
                        field_name, field_info, types
                    )
                )
                .flat_map(lambda data: converter.build_cli_param_spec(field_name, data))
            )

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
                            converter = FlextCliModels.CliModelConverter
                            return converter.pydantic_type_to_python_type(arg)

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
                FlextResult containing CLI parameter specification

            """
            try:
                # Railway pattern: validate → convert types →
                # extract properties → build spec (public API)
                return FlextCliModels.CliModelConverter.convert_field_to_cli_param(
                    field_name, field_info
                )
            except Exception as e:
                return FlextResult[FlextCliModels.CliParameterSpec].fail(
                    FlextCliConstants.ModelsErrorMessages.FAILED_FIELD_CONVERSION.format(
                        field_name=field_name, error=str(e)
                    )
                )

        @staticmethod
        def validate_field_type(
            field_name: str, field_info: fields.FieldInfo
        ) -> FlextResult[type]:
            """Validate field has type annotation."""
            field_type = field_info.annotation
            if field_type is None:
                return FlextResult[type].fail(
                    FlextCliConstants.ModelsErrorMessages.FIELD_NO_TYPE_ANNOTATION.format(
                        field_name=field_name
                    )
                )
            return FlextResult[type].ok(field_type)

        @staticmethod
        def convert_field_types(
            field_type: type,
        ) -> FlextResult[FieldMetadataDict]:
            """Convert Pydantic type to Python and Click types."""
            python_type = FlextCliModels.CliModelConverter.pydantic_type_to_python_type(
                field_type
            )
            click_type = FlextCliModels.CliModelConverter.python_type_to_click_type(
                python_type
            )
            return FlextResult[FieldMetadataDict].ok({
                "python_type": python_type,
                "click_type": click_type,
            })

        @staticmethod
        def extract_field_properties(
            field_name: str,
            field_info: fields.FieldInfo,
            types: FieldMetadataDict,
        ) -> FlextResult[FieldMetadataDict]:
            """Extract all field properties (defaults, description, metadata)."""
            # Extract defaults
            is_required = field_info.default is PydanticUndefined
            default_value = None if is_required else field_info.default

            # Extract description
            # Validate description explicitly - no fallback
            description = (
                field_info.description
                if field_info.description is not None
                else FlextCliConstants.ModelsDefaults.DEFAULT_FIELD_DESCRIPTION.format(
                    field_name=field_name
                )
            )

            # Extract metadata
            validators: list[
                Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]
            ] = []
            metadata: dict[str, FlextTypes.JsonValue] = {}

            if hasattr(field_info, "metadata"):
                for meta_item in field_info.metadata:
                    if hasattr(meta_item, "__dict__"):
                        metadata.update(meta_item.__dict__)

            # Combine all data
            return FlextResult[FieldMetadataDict].ok({
                **types,
                "is_required": is_required,
                "default_value": default_value,
                "description": description,
                "validators": validators,
                "metadata": metadata,
            })

        @staticmethod
        def _validate_field_data(
            field_name: str, data: FieldMetadataDict
        ) -> FlextResult[FieldValidationResult]:
            """Validate and extract field data components."""
            python_type = data["python_type"]
            if not isinstance(python_type, type):
                return FlextResult[FieldValidationResult].fail(
                    f"Invalid python_type for field {field_name}: "
                    f"expected type, got {type(python_type)}"
                )

            click_type = data["click_type"]
            if not isinstance(click_type, str):
                return FlextResult[FieldValidationResult].fail(
                    f"Invalid click_type for field {field_name}: "
                    f"expected str, got {type(click_type)}"
                )

            is_required = data["is_required"]
            if not isinstance(is_required, bool):
                return FlextResult[FieldValidationResult].fail(
                    f"Invalid is_required for field {field_name}: "
                    f"expected bool, got {type(is_required)}"
                )

            description = data["description"]
            if not isinstance(description, str):
                return FlextResult[FieldValidationResult].fail(
                    f"Invalid description for field {field_name}: "
                    f"expected str, got {type(description)}"
                )

            validators_raw = data["validators"]
            if not isinstance(validators_raw, list):
                return FlextResult[FieldValidationResult].fail(
                    f"Invalid validators for field {field_name}: "
                    f"expected list, got {type(validators_raw)}"
                )

            metadata_raw = data["metadata"]
            if not isinstance(metadata_raw, dict):
                return FlextResult[FieldValidationResult].fail(
                    f"Invalid metadata for field {field_name}: "
                    f"expected dict, got {type(metadata_raw)}"
                )

            # Type cast to ensure correct types
            # validators_raw is already validated as list, cast to correct type
            validators: list[Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]] = (
                validators_raw  # type: ignore[assignment]
            )
            # metadata_raw is already validated as dict, cast to correct type
            metadata: dict[str, FlextTypes.JsonValue] = metadata_raw  # type: ignore[assignment]

            return FlextResult[FieldValidationResult].ok((
                python_type,
                click_type,
                is_required,
                description,
                validators,
                metadata,
            ))

        @staticmethod
        def _process_validators(
            validators_raw: list[object],
        ) -> list[Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]]:
            """Process and type-narrow validators list."""
            validators: list[
                Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]
            ] = []
            for validator in validators_raw:
                if callable(validator):
                    typed_validator = typing.cast(
                        "Callable[[FlextTypes.JsonValue], FlextTypes.JsonValue]",
                        validator,
                    )
                    validators.append(typed_validator)
            return validators

        @staticmethod
        def _process_metadata(
            metadata_raw: dict[str, object],
        ) -> dict[str, FlextTypes.JsonValue]:
            """Process and type-narrow metadata dict."""
            return {
                key: value
                for key, value in metadata_raw.items()
                if isinstance(key, str)
                and isinstance(value, (str, int, float, bool, dict, list, type(None)))
            }

        @staticmethod
        def build_cli_param_spec(
            field_name: str, data: FieldMetadataDict
        ) -> FlextResult[FlextCliModels.CliParameterSpec]:
            """Build CLI parameter specification from extracted data."""
            # Extract and type-narrow default value
            default_value_raw = data["default_value"]
            default_value: FlextTypes.JsonValue | None = None
            if default_value_raw is not None and isinstance(
                default_value_raw, (str, int, float, bool, dict, list, type(None))
            ):
                default_value = typing.cast("FlextTypes.JsonValue", default_value_raw)

            # Validate and extract field data
            # SLF001: Accessing private method is intentional - it's a static method within the same class
            validation_result = FlextCliModels.CliModelConverter._validate_field_data(  # noqa: SLF001
                field_name, data
            )
            if validation_result.is_failure:
                return FlextResult[FlextCliModels.CliParameterSpec].fail(
                    validation_result.error
                )

            (
                python_type,
                click_type,
                is_required,
                description,
                validators_raw,
                metadata_raw,
            ) = validation_result.unwrap()

            # Process validators and metadata
            # Type cast: validators_raw is already validated as list[Callable[...]]
            # SLF001: Accessing private method is intentional - it's a static method within the same class
            validators = FlextCliModels.CliModelConverter._process_validators(  # noqa: SLF001
                list(validators_raw)
            )
            # Type cast: metadata_raw is already validated as dict[str, JsonValue]
            # SLF001: Accessing private method is intentional - it's a static method within the same class
            metadata = FlextCliModels.CliModelConverter._process_metadata(  # noqa: SLF001
                dict(metadata_raw)
            )

            # Build and return CLI parameter spec
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

        @staticmethod
        def model_to_cli_params(
            model_class: type[BaseModel],
        ) -> FlextResult[list[FlextCliModels.CliParameterSpec]]:
            """Extract all fields from Pydantic model and convert to CLI parameters.

            Args:
                model_class: Pydantic model class to convert

            Returns:
                FlextResult containing list of comprehensive CLI parameter
                specifications

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
                    option_name = (
                        f"{FlextCliConstants.CliParamDefaults.OPTION_PREFIX}"
                        f"{param.name}"
                    )

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
            cli_args: FlextTypes.JsonDict,
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

        Provides decorators that automatically generate CLI commands
        from Pydantic models, eliminating manual parameter declaration
        boilerplate.

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
                # Fast fail - use func.__name__ if command_name is None
                final_command_name = (
                    func.__name__ if command_name is None else command_name
                )
                setattr(
                    func,
                    FlextCliConstants.CliParamDefaults.MAGIC_ATTR_CLI_COMMAND_NAME,
                    final_command_name,
                )

                def wrapper(
                    **cli_kwargs: FlextTypes.JsonValue,
                ) -> FlextTypes.JsonValue | FlextResult[object]:
                    # Validate CLI input with Pydantic model
                    # kwargs is always a dict, type is correct
                    validation_result = (
                        FlextCliModels.CliModelConverter.cli_args_to_model(
                            model_class, cli_kwargs
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
                # Fast fail - use func.__name__ if command_name is None
                final_command_name = (
                    func.__name__ if command_name is None else command_name
                )
                setattr(
                    func,
                    FlextCliConstants.CliParamDefaults.MAGIC_ATTR_CLI_COMMAND_NAME,
                    final_command_name,
                )

                def wrapper(
                    **cli_kwargs: FlextTypes.JsonValue,
                ) -> FlextTypes.JsonValue | FlextResult[object]:
                    validated_models: list[BaseModel] = []

                    # Validate with each model
                    for model_class in model_classes:
                        # kwargs is always a dict, type is correct
                        validation_result = (
                            FlextCliModels.CliModelConverter.cli_args_to_model(
                                model_class, cli_kwargs
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
    # CLI BUILDERS - Model and Option Construction Utilities
    # =========================================================================

    class ModelCommandBuilder:
        """Build CLI commands from Pydantic models.

        Single Responsibility: Convert Pydantic models to executable CLI commands.
        Extracted from cli.py to follow Single Responsibility Principle and nested
        in FlextCliModels following flext-core patterns.
        """

        def __init__(
            self,
            model_class: type[BaseModel],
            handler: Callable[..., FlextTypes.JsonValue],
            config: FlextCliConfig | None = None,
        ) -> None:
            """Initialize builder.

            Args:
                model_class: Pydantic model class
                handler: Handler function to call with model instance
                config: Optional config to integrate

            """
            self.model_class = model_class
            self.handler = handler
            self.config = config
            self.params_def: list[str] = []
            self.params_call: list[str] = []
            self.field_mapping: dict[str, str] = {}

        def build(self) -> Callable[..., None]:
            """Build the command function.

            Returns:
                Callable command function

            """
            self._build_parameters()
            func = self._generate_function()

            if self.config is not None:
                return self._wrap_with_config_update(func)

            return func

        def _resolve_field_type(self, field_name: str) -> type:
            """Resolve field type, handling ForwardRefs and Annotated types.

            Args:
                field_name: Name of the field to resolve

            Returns:
                Resolved base type suitable for CLI (unwraps Annotated, resolves ForwardRefs)

            """
            try:
                # Use get_type_hints to resolve ForwardRefs
                type_hints = get_type_hints(self.model_class)
                resolved_type = type_hints.get(field_name, str)

                # Unwrap Annotated[T, ...] to get base type T
                origin = get_origin(resolved_type)
                if origin is Annotated:
                    args = get_args(resolved_type)
                    if args:
                        # Type narrowing: first arg is the base type
                        base_type = args[0]
                        if isinstance(base_type, type):
                            return base_type

                # Type narrowing: resolved_type should be a type
                if isinstance(resolved_type, type):
                    return resolved_type
                return str
            except (NameError, AttributeError):
                # Fast-fail: type resolution failed
                # Validate annotation explicitly - no fallback
                annotation = self.model_class.model_fields[field_name].annotation
                # Fast-fail if annotation is None - no fallback
                if annotation is None:
                    return str
                return annotation

        def _build_parameters(self) -> None:
            """Build parameter definitions from model fields."""
            for field_name, field_info in self.model_class.model_fields.items():
                # Use Pydantic v2 Field alias if defined, otherwise convert underscores to hyphens
                # Validate explicitly - no fallback
                if field_info.alias is not None:
                    param_name = field_info.alias
                else:
                    param_name = field_name.replace("_", "-")
                self.field_mapping[param_name] = field_name

                # Resolve field type (handles ForwardRefs and Annotated)
                field_type = self._resolve_field_type(field_name)
                type_str = self._format_type_annotation(field_type)

                # Build typer.Option specification
                default_value = self._get_field_default(field_name, field_info)
                is_required = field_info.is_required()
                # Validate description explicitly - no fallback
                help_text = (
                    field_info.description if field_info.description is not None else ""
                )

                # Generate parameter definition
                # Special handling for boolean fields: use --flag/--no-flag syntax
                is_boolean = field_type is bool or (
                    get_origin(field_type) is typing.Union
                    and bool in get_args(field_type)
                )

                if is_required:
                    self.params_def.append(
                        f"{param_name}: {type_str} = typer.Option(..., help={help_text!r})"
                    )
                elif is_boolean:
                    # Boolean fields automatically get --flag/--no-flag in Typer
                    # by using the field name with underscores replaced by hyphens
                    self.params_def.append(
                        f"{param_name}: {type_str} = typer.Option("
                        f"{default_value!r}, '--{param_name}/--no-{param_name}', "
                        f"help={help_text!r})"
                    )
                else:
                    self.params_def.append(
                        f"{param_name}: {type_str} = typer.Option("
                        f"{default_value!r}, help={help_text!r})"
                    )

                self.params_call.append(f"{field_name}={param_name}")

        @staticmethod
        def _format_type_annotation(annotation: type | types.UnionType | None) -> str:
            """Format type annotation for CLI help text.

            Args:
                annotation: Type annotation to format

            Returns:
                str: Human-readable type string

            """
            if annotation is None:
                return "unknown"
            if isinstance(annotation, type):
                return annotation.__name__
            return str(annotation)

        def _get_field_default(
            self, field_name: str, field_info: fields.FieldInfo
        ) -> FlextTypes.JsonValue | None:
            """Get default value for field using fast-fail pattern.

            Tries in order: config → field default → default factory
            Fast-fails if no default available (returns None - field is required)

            Args:
                field_name: Name of the field
                field_info: Pydantic FieldInfo

            Returns:
                Default value or None if no default available (field is required)

            """
            # Fast-fail pattern: try config first
            config_result = self._try_config_default(field_name)
            if config_result.is_success:
                return config_result.unwrap()

            # Try field default
            field_result = self._try_field_default(field_info)
            if field_result.is_success:
                return field_result.unwrap()

            # Try default factory
            factory_result = self._try_default_factory(field_info)
            if factory_result.is_success:
                return factory_result.unwrap()

            # No default available - field is required (fast-fail, no fallback)
            return None

        def _try_config_default(
            self, field_name: str
        ) -> FlextResult[FlextTypes.JsonValue]:
            """Try to get default from config attribute."""
            # Fast fail validation
            if self.config is None:
                return FlextResult[FlextTypes.JsonValue].fail("No config value")
            if not hasattr(self.config, field_name):
                return FlextResult[FlextTypes.JsonValue].fail("No config value")

            value = getattr(self.config, field_name)
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                return FlextResult[FlextTypes.JsonValue].ok(value)
            return FlextResult[FlextTypes.JsonValue].ok(str(value))

        def _try_field_default(
            self, field_info: fields.FieldInfo
        ) -> FlextResult[FlextTypes.JsonValue]:
            """Try to get default from field definition."""
            if field_info.default is PydanticUndefined:
                return FlextResult[FlextTypes.JsonValue].fail("No field default")

            default = field_info.default
            if default is None:
                return FlextResult[FlextTypes.JsonValue].fail("Field default is None")
            if isinstance(default, (str, int, float, bool, list, dict)):
                return FlextResult[FlextTypes.JsonValue].ok(default)
            return FlextResult[FlextTypes.JsonValue].ok(str(default))

        def _try_default_factory(
            self, field_info: fields.FieldInfo
        ) -> FlextResult[FlextTypes.JsonValue]:
            """Try to get default from factory callable."""
            default_factory = field_info.default_factory
            # Fast fail validation
            if default_factory is None:
                return FlextResult[FlextTypes.JsonValue].fail("No factory")
            if not callable(default_factory):
                return FlextResult[FlextTypes.JsonValue].fail("No factory")

            if not self._factory_accepts_no_arguments(default_factory):
                return FlextResult[FlextTypes.JsonValue].fail("Factory needs arguments")

            # Type narrowing: default_factory is callable with no required args
            # Call factory - validated above that it accepts no arguments
            # Use typing.cast to help type checker understand the signature
            factory_callable = typing.cast("Callable[[], object]", default_factory)
            try:
                factory_result = factory_callable()
            except (TypeError, ValueError) as e:
                return FlextResult[FlextTypes.JsonValue].fail(
                    f"Factory call failed: {e}"
                )

            if isinstance(
                factory_result, (str, int, float, bool, list, dict, type(None))
            ):
                return FlextResult[FlextTypes.JsonValue].ok(factory_result)
            return FlextResult[FlextTypes.JsonValue].ok(str(factory_result))

        @staticmethod
        def _factory_accepts_no_arguments(factory: Callable[..., object]) -> bool:
            """Return True when callable can be invoked without required arguments."""
            signature = inspect.signature(factory)
            for parameter in signature.parameters.values():
                if parameter.kind in {
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                }:
                    continue
                if parameter.default is inspect.Parameter.empty:
                    return False
            return True

        def _generate_function(self) -> Callable[..., None]:
            """Generate the command function with Pydantic v2 Field alias support.

            Creates a function with typer.Option() that respects Field aliases
            for CLI option names (e.g., --input-dir instead of --input_dir).

            Returns:
                Generated function with proper CLI parameter names

            """
            # Capture model_class, handler, and field_mapping in closure
            model_class = self.model_class
            handler = self.handler
            field_mapping = self.field_mapping

            # Build parameters with typer.Option for each field
            # We create a dictionary of parameters where:
            # - key = field_name (Python parameter name with underscores)
            # - value = typer.Option instance with CLI name (with hyphens if aliased)
            parameters = []

            for cli_param, field_name in field_mapping.items():
                field_info = self.model_class.model_fields.get(field_name)
                if not field_info:
                    continue

                # Get default value and metadata
                default_value = self._get_field_default(field_name, field_info)
                is_required = field_info.is_required()
                # Validate description explicitly - no fallback
                help_text = (
                    field_info.description if field_info.description is not None else ""
                )

                # Resolve field type (handles ForwardRefs and Annotated)
                resolved_type = self._resolve_field_type(field_name)

                # Check if field is boolean for automatic --flag/--no-flag generation
                is_boolean = resolved_type is bool or (
                    get_origin(resolved_type) is typing.Union
                    and bool in get_args(resolved_type)
                )

                # Create typer.Option with explicit CLI name
                # For boolean fields, use --flag/--no-flag syntax automatically
                if is_required:
                    option_default = typer.Option(
                        ...,
                        f"--{cli_param}",  # Explicit CLI name with hyphens
                        help=help_text,
                    )
                elif is_boolean:
                    # Boolean fields get automatic --flag/--no-flag syntax
                    option_default = typer.Option(
                        default_value,
                        f"--{cli_param}/--no-{cli_param}",  # Boolean flag syntax
                        help=help_text,
                    )
                else:
                    option_default = typer.Option(
                        default_value,
                        f"--{cli_param}",  # Explicit CLI name with hyphens
                        help=help_text,
                    )

                # Create Parameter with field_name (underscores) and typer.Option default
                param = inspect.Parameter(
                    field_name,  # Python parameter name (underscores)
                    inspect.Parameter.KEYWORD_ONLY,
                    default=option_default,  # typer.Option with CLI name
                    annotation=resolved_type,
                )
                parameters.append(param)

            def generated_command(**kwargs: FlextTypes.JsonValue) -> None:
                """Dynamically generated command function.

                Uses closure to capture model_class, handler, and field_mapping
                without requiring exec or eval.
                """
                # Build model arguments from CLI kwargs
                # kwargs keys are field_names (underscores), not cli_params (hyphens)
                model_args: FlextTypes.JsonDict = {}
                for field_name, value in kwargs.items():
                    if value is not None:
                        model_args[field_name] = value

                # Create model instance and call handler
                model_instance = model_class(**model_args)
                handler(model_instance)

            # Assign signature to function for Typer introspection
            # Set signature directly - all callables support __signature__ attribute
            signature = inspect.Signature(parameters)
            # Use setattr to avoid type checker issues with dynamic attributes
            # B010: setattr with constant - this is intentional for dynamic attribute assignment
            setattr(generated_command, "__signature__", signature)  # noqa: B010

            return generated_command

        def _wrap_with_config_update(
            self, func: Callable[..., None]
        ) -> Callable[..., None]:
            """Wrap function to update config with CLI values.

            Args:
                func: Function to wrap

            Returns:
                Wrapped function

            """

            @functools.wraps(func)
            def wrapped(**kwargs: FlextTypes.JsonValue) -> None:
                """Update config and call wrapped function."""
                if self.config is not None:
                    # Update config fields from CLI args
                    # Only update fields that exist in config (command-specific params are ignored)
                    for cli_param, field_name in self.field_mapping.items():
                        # Fast-fail: validate param exists in kwargs before accessing
                        if cli_param not in kwargs:
                            continue
                        cli_value = kwargs[cli_param]
                        if cli_value is not None and hasattr(self.config, field_name):
                            setattr(self.config, field_name, cli_value)

                func(**kwargs)

            # Preserve signature from wrapped function for Click/Typer introspection
            if hasattr(func, "__signature__"):
                func_signature = getattr(func, "__signature__", None)
                if func_signature is not None:
                    # Use setattr to avoid type checker issues with dynamic attributes
                    # B010: setattr with constant - this is intentional for dynamic attribute assignment
                    setattr(wrapped, "__signature__", func_signature)  # noqa: B010

            return wrapped

    class OptionBuilder:
        """Build typer.Option from FlextCliConfig field metadata.

        Single Responsibility: Convert Pydantic field metadata to typer.Option.
        Extracted from cli_params.py to follow Single Responsibility Principle and nested
        in FlextCliModels following flext-core patterns.
        """

        def __init__(
            self,
            field_name: str,
            registry: dict[str, dict[str, str | int | bool | list[str]]],
        ) -> None:
            """Initialize builder.

            Args:
                field_name: Name of field in FlextCliConfig
                registry: CLI parameter registry with metadata

            """
            self.field_name = field_name
            self.registry = registry

            # Get field metadata
            self.fields = FlextCliConfig.model_fields
            self.schema = FlextCliConfig.model_json_schema()

            if field_name not in self.fields:
                msg = f"Field {field_name!r} not found in FlextCliConfig"
                raise ValueError(msg)

            self.field_info = self.fields[field_name]

            # Validate schema properties exist - no fallback
            schema_properties = self.schema.get("properties")
            if schema_properties is None:
                error_msg = "Schema missing 'properties' key"
                raise ValueError(error_msg)
            if field_name not in schema_properties:
                error_msg = f"Field {field_name!r} not found in schema properties"
                raise ValueError(error_msg)
            self.field_schema = schema_properties[field_name]

            # Validate registry entry exists - no fallback
            if field_name not in registry:
                error_msg = f"Field {field_name!r} not found in registry"
                raise ValueError(error_msg)
            self.param_meta = registry[field_name]

        def build(self) -> OptionInfo:
            """Build typer.Option from field metadata.

            Returns:
                typer.Option instance

            """
            param_decls = self._build_param_declarations()
            default_value = self._get_default_value()
            help_text = self._build_help_text()
            constraints = self._extract_constraints()

            # Extract constraint values with proper types for typer.Option
            case_sensitive_val = constraints.get("case_sensitive", True)
            case_sensitive = (
                bool(case_sensitive_val) if case_sensitive_val is not None else True
            )

            min_val = constraints.get("min")
            min_constraint: int | float | None = None
            if min_val is None:
                min_constraint = None
            elif isinstance(min_val, int):
                min_constraint = int(min_val)
            elif isinstance(min_val, float):
                min_constraint = float(min_val)

            max_val = constraints.get("max")
            max_constraint: int | float | None = None
            if max_val is None:
                max_constraint = None
            elif isinstance(max_val, int):
                max_constraint = int(max_val)
            elif isinstance(max_val, float):
                max_constraint = float(max_val)

            # typer.Option returns OptionInfo
            option_info: OptionInfo = typer.Option(
                default_value,
                *param_decls,
                help=help_text,
                case_sensitive=case_sensitive,
                min=min_constraint,
                max=max_constraint,
                show_default=default_value is not None,
            )
            return option_info

        def _extract_type(self) -> type | types.UnionType:
            """Extract base type from field annotation."""
            field_type = FlextCliUtilities.TypeNormalizer.normalize_annotation(
                self.field_info.annotation
            )

            # Guard against None
            if field_type is None:
                return str

            origin = get_origin(field_type)

            # Handle Optional types
            if origin is types.NoneType or (
                hasattr(field_type, "__args__")
                and types.NoneType in get_args(field_type)
            ):
                args = [a for a in get_args(field_type) if a is not types.NoneType]
                return args[0] if args else str

            return field_type

        def _build_param_declarations(self) -> list[str]:
            """Build parameter declarations (--name, -short)."""
            reg = FlextCliConstants.CliParamsRegistry

            cli_name = self.param_meta.get(reg.KEY_FIELD_NAME_OVERRIDE, self.field_name)
            cli_name = str(cli_name) if cli_name != self.field_name else self.field_name

            # Build long form (--param-name)
            option_name = f"--{cli_name.replace('_', '-')}"
            param_decls = [option_name]

            # Add short form if available (-p)
            if reg.KEY_SHORT in self.param_meta:
                short_val = self.param_meta[reg.KEY_SHORT]
                if isinstance(short_val, str):
                    param_decls.insert(0, f"-{short_val}")

            return param_decls

        def _get_default_value(self) -> FlextTypes.JsonValue:
            """Get default value from field."""
            default_value = self.field_info.default

            if default_value is None:
                return None

            if isinstance(default_value, type(PydanticUndefined)):
                return None

            # Validate that default is a JSON-compatible value
            if isinstance(
                default_value, (str, int, float, bool, list, dict, type(None))
            ):
                return default_value

            # For other types, convert to string representation
            return str(default_value)

        def _build_help_text(self) -> str:
            """Build help text from field description and metadata."""
            defs = FlextCliConstants.CliParamsDefaults
            reg = FlextCliConstants.CliParamsRegistry
            json_keys = FlextCliConstants.JsonSchemaKeys

            help_text = (
                self.field_info.description
                or defs.DEFAULT_HELP_TEXT_FORMAT.format(field_name=self.field_name)
            )

            # Add choices to help text
            if reg.KEY_CHOICES in self.param_meta:
                choices = self.param_meta[reg.KEY_CHOICES]
                if isinstance(choices, (list, tuple)):
                    choices_str = ", ".join(str(c) for c in choices)
                    help_text += defs.CHOICES_HELP_SUFFIX.format(
                        choices_str=choices_str
                    )

            # Add range constraints to help text
            if (
                json_keys.MINIMUM in self.field_schema
                and json_keys.MAXIMUM in self.field_schema
            ):
                help_text += defs.RANGE_HELP_SUFFIX.format(
                    minimum=self.field_schema[json_keys.MINIMUM],
                    maximum=self.field_schema[json_keys.MAXIMUM],
                )

            return help_text

        def _extract_constraints(self) -> dict[str, FlextTypes.JsonValue]:
            """Extract constraints (min, max, case_sensitive)."""
            reg = FlextCliConstants.CliParamsRegistry
            json_keys = FlextCliConstants.JsonSchemaKeys

            constraints: dict[str, FlextTypes.JsonValue] = {}

            # Case sensitivity
            if reg.KEY_CASE_SENSITIVE in self.param_meta:
                cs_raw = self.param_meta[reg.KEY_CASE_SENSITIVE]
                if isinstance(cs_raw, bool):
                    constraints["case_sensitive"] = cs_raw

            # Min/Max constraints
            if json_keys.MINIMUM in self.field_schema:
                min_raw = self.field_schema[json_keys.MINIMUM]
                if isinstance(min_raw, (int, float)):
                    constraints["min"] = min_raw

            if json_keys.MAXIMUM in self.field_schema:
                max_raw = self.field_schema[json_keys.MAXIMUM]
                if isinstance(max_raw, (int, float)):
                    constraints["max"] = max_raw

            return constraints

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
        - Literal types for enum values (eliminates field_validator)
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
        # REFACTORED: Use Literal from constants instead of field_validator
        # Provides type safety + runtime validation without custom validator
        status: FlextCliConstants.CommandStatusLiteral = Field(
            default="pending",
            description=FlextCliConstants.CliCommandDescriptions.STATUS,
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
                "is_completed": bool(self.is_completed),
                "is_successful": bool(self.is_successful),
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

        @field_serializer("command_line")  # type: ignore[type-var]
        def serialize_command_line(self, value: str, _info: fields.FieldInfo) -> str:
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
            cls, data: FlextTypes.JsonValue
        ) -> FlextResult[FlextCliTypes.Data.CliCommandData]:
            """Validate and normalize command input data using railway pattern.

            Args:
                data: Command input data to validate

            Returns:
                FlextResult with validated and normalized data (never None)

            """
            # Extract command from data - ensure it's a string
            if not isinstance(data, dict):
                return FlextResult[FlextCliTypes.Data.CliCommandData].fail(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_DATA_MUST_BE_DICT
                )

            # Type narrowing: data is dict[str, JsonValue] after isinstance check

            if "command" not in data:
                return FlextResult[FlextCliTypes.Data.CliCommandData].fail(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_FIELD_REQUIRED
                )

            command = data.pop("command")
            if not isinstance(command, str):
                return FlextResult[FlextCliTypes.Data.CliCommandData].fail(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_MUST_BE_STRING
                )

            # Normalize command data
            # Type narrow: ensure all values are JsonValue compatible
            normalized_data: FlextCliTypes.Data.CliDataDict = {
                "command": command,
            }
            # Add execution_time if present and valid
            exec_time = data.get("execution_time")
            if exec_time is not None and isinstance(
                exec_time, (str, int, float, bool, dict, list, type(None))
            ):
                normalized_data["execution_time"] = exec_time
            # Add other fields that are JsonValue compatible
            for k, v in data.items():
                if k not in {"command", "execution_time"} and isinstance(
                    v, (str, int, float, bool, dict, list, type(None))
                ):
                    normalized_data[k] = v

            # Return normalized data (type is already correct, never None)
            return FlextResult[FlextCliTypes.Data.CliCommandData].ok(normalized_data)

        def start_execution(self) -> FlextResult[bool]:
            """Start command execution.

            Returns:
                FlextResult[bool]: True if execution started successfully, failure on error

            """
            state_result = (
                FlextCliMixins.BusinessRulesMixin.validate_command_execution_state(
                    self.status,
                    FlextCliConstants.CommandStatus.PENDING.value,
                    "start execution",
                )
            )
            if not state_result.is_success:
                return state_result

            self.status = "running"  # Literal type requires exact string
            return FlextResult[bool].ok(True)

        def complete_execution(
            self, exit_code: int, output: str = ""
        ) -> FlextResult[bool]:
            """Complete command execution.

            Returns:
                FlextResult[bool]: True if execution completed successfully, failure on error

            """
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
            self.status = "completed"  # Literal type requires exact string
            return FlextResult[bool].ok(True)

        @classmethod
        def __init_subclass__(cls, **kwargs: object) -> None:
            """Automatically rebuild model for forward references in Pydantic v2."""
            # BaseModel.__init_subclass__ accepts keyword arguments but mypy strict doesn't recognize it
            # This is a known limitation - BaseModel.__init_subclass__ does accept **kwargs
            # We need to call it without **kwargs to satisfy mypy, but Pydantic accepts it at runtime
            super().__init_subclass__()
            if hasattr(cls, "model_rebuild"):
                cls.model_rebuild()

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
        - Literal types for enum values (eliminates field_validator)
        - model_validator for cross-field validation
        """

        # Session-specific fields (id, created_at, updated_at inherited from Entity)
        # Using Annotated with StringConstraints for automatic validation
        session_id: Annotated[
            str, StringConstraints(min_length=1, strip_whitespace=True)
        ] = Field(
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
        # REFACTORED: Use Literal for status instead of field_validator
        # Provides type safety + runtime validation without custom validator
        status: FlextCliConstants.SessionStatusLiteral = Field(
            default="active",
            description=FlextCliConstants.CliSessionDescriptions.STATUS,
        )
        # Using Annotated with StringConstraints for automatic validation
        # Use empty string as default instead of None - Config can override if needed
        user_id: str = Field(
            default=FlextCliConstants.CliSessionDefaults.DEFAULT_USER_ID,
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
                has_user=bool(self.user_id),
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

            return self

        @field_serializer("commands")  # type: ignore[type-var]
        def serialize_commands(
            self, value: list[FlextCliModels.CliCommand], _info: fields.FieldInfo
        ) -> list[FlextTypes.JsonDict]:
            """Serialize commands with summary information."""
            return [
                {
                    "id": str(getattr(cmd, "id", "")),
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

        def add_command(self, command: FlextCliModels.CliCommand) -> FlextResult[bool]:
            """Add a command to the session.

            Returns:
                FlextResult[bool]: True if command added successfully, failure on error

            """
            if command in self.commands:
                return FlextResult[bool].fail(
                    FlextCliConstants.ModelsErrorMessages.COMMAND_ALREADY_EXISTS
                )

            self.commands.append(command)
            self.commands_executed = len(self.commands)
            return FlextResult[bool].ok(True)

    class DebugInfo(FlextModels.ArbitraryTypesModel):
        """Debug information model with comprehensive diagnostic data.

        Extends FlextModels.ArbitraryTypesModel for strict validation.

        Pydantic 2.11 Features:
        - Annotated fields with StringConstraints (eliminates validate_service)
        - Literal types for enum values (eliminates status validator)
        - computed_field for derived properties
        - field_validator for business logic (level normalization)
        - field_serializer for sensitive data masking
        """

        # REFACTORED: Use StringConstraints instead of validate_service
        service: Annotated[
            str, StringConstraints(min_length=1, strip_whitespace=True)
        ] = Field(
            default=FlextCliConstants.DebugServiceNames.DEBUG,
            description=FlextCliConstants.DebugInfoDescriptions.SERVICE,
            examples=["FlextCliDebug", "FlextCliCore", "FlextCliCommands"],
        )
        # REFACTORED: Use Literal for status instead of field_validator
        status: FlextCliConstants.ServiceStatusLiteral = Field(
            default="operational",
            description=FlextCliConstants.DebugInfoDescriptions.STATUS,
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

        # Pydantic 2.11 field validators - Keep level validator for normalization
        @field_validator("level")
        @classmethod
        def validate_level(cls, v: str) -> str:
            """Validate debug level is valid using Pydantic 2 field_validator.

            Accepts case-insensitive input and normalizes to uppercase.
            """
            valid_levels = [
                FlextConstants.Logging.DEBUG,
                FlextConstants.Logging.INFO,
                FlextConstants.Logging.WARNING,
                FlextConstants.Logging.ERROR,
                FlextConstants.Logging.CRITICAL,
            ]
            # Normalize to uppercase for case-insensitive comparison
            normalized = v.upper()
            if normalized not in valid_levels:
                valid_options = ", ".join(valid_levels)
                msg = f"invalid debug level: {v}. valid options: {valid_options}"
                raise ValueError(msg)
            return normalized

        # Pydantic 2.11 computed fields
        @computed_field
        def total_stats(self) -> int:
            """Total count of diagnostic statistics."""
            return len(self.system_info) + len(self.config_info)

        @computed_field
        def has_diagnostics(self) -> bool:
            """Check if debug info contains diagnostic data."""
            # Fast fail - check each condition separately
            has_system = bool(self.system_info)
            has_config = bool(self.config_info)
            return has_system or has_config

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

        @field_serializer("system_info", "config_info")  # type: ignore[type-var]
        def serialize_sensitive_info(
            self, value: dict[str, str], _info: fields.FieldInfo
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

    class LoggingConfig(FlextModels.ArbitraryTypesModel):
        """Logging configuration model for CLI operations.

        Extends FlextModels.ArbitraryTypesModel for flexible configuration.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        """

        log_level: FlextCliConstants.LogLevelLiteral = Field(
            default="INFO",
            description=FlextCliConstants.LoggingConfigDescriptions.LOG_LEVEL,
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

    class CliCommandResult(FlextModels.ArbitraryTypesModel):
        """CLI command result model - replaces FlextTypes.JsonDict in command execution results.

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

    class CliDebugData(FlextModels.ArbitraryTypesModel):
        """CLI debug data model - replaces FlextTypes.JsonDict in debug information.

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

    class CliSessionData(FlextModels.ArbitraryTypesModel):
        """CLI session data model - replaces FlextTypes.JsonDict in session summaries.

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
        """CLI logging data model - replaces FlextTypes.JsonDict in logging summaries.

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

    class TableConfig(FlextModels.ArbitraryTypesModel):
        """Table configuration model - consolidates 12 parameters into validated config object.

        Replaces multiple parameters in create_table() with single Pydantic model,
        providing validation, defaults from constants, and better maintainability.
        """

        table_format: str = Field(
            default=FlextCliConstants.TableFormats.SIMPLE,
            description="Table format (grid, simple, pipe, etc.)",
        )
        headers: str | typing.Sequence[str] = Field(
            default=FlextCliConstants.TableFormats.KEYS,
            description="Column headers ('keys', 'firstrow', or list)",
        )
        align: str | typing.Sequence[str] | None = Field(
            default=None,
            description="Column alignment (left, right, center, decimal)",
        )
        floatfmt: str = Field(
            default=FlextCliConstants.TablesDefaults.DEFAULT_FLOAT_FORMAT,
            description="Float number formatting",
        )
        numalign: str = Field(
            default=FlextCliConstants.TablesDefaults.DEFAULT_NUM_ALIGN,
            description="Number alignment",
        )
        stralign: str = Field(
            default=FlextCliConstants.TablesDefaults.DEFAULT_STR_ALIGN,
            description="String alignment",
        )
        missingval: str = Field(
            default=FlextCliConstants.TablesDefaults.DEFAULT_MISSING_VALUE,
            description="Value for missing data",
        )
        showindex: bool | str = Field(
            default=False,
            description="Show row index (bool or index name)",
        )
        disable_numparse: bool = Field(
            default=False,
            description="Disable automatic number parsing",
        )
        colalign: typing.Sequence[str] | None = Field(
            default=None,
            description="Column alignment per column",
        )

        def get_effective_colalign(self) -> typing.Sequence[str] | None:
            """Compute effective column alignment based on colalign and align.

            Returns:
                Sequence of alignment strings or None

            """
            if self.colalign is not None:
                return self.colalign
            if self.align is not None and not isinstance(self.align, str):
                return self.align
            return None

    class CliParamsConfig(FlextModels.ArbitraryTypesModel):
        """CLI parameters configuration model - consolidates 8 CLI parameters.

        Replaces multiple parameters in apply_to_config() with single Pydantic model,
        providing validation, defaults, and better maintainability.

        CRITICAL: None values mean "don't change from Config", but when creating
        instances, values from Config are used as defaults (Config has priority over Constants).
        """

        verbose: bool | None = Field(
            default=None,
            description="Verbose output flag from CLI (None = use Config value)",
        )
        quiet: bool | None = Field(
            default=None,
            description="Quiet mode flag from CLI (None = use Config value)",
        )
        debug: bool | None = Field(
            default=None,
            description="Debug mode flag from CLI (None = use Config value)",
        )
        trace: bool | None = Field(
            default=None,
            description="Trace mode flag from CLI (None = use Config value)",
        )
        log_level: str | None = Field(
            default=None,
            description="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL, None = use Config value)",
        )
        log_format: str | None = Field(
            default=None,
            description="Log format (compact/detailed/full, None = use Config value)",
        )
        output_format: str | None = Field(
            default=None,
            description="Output format (json/yaml/csv/table/plain, None = use Config value)",
        )
        no_color: bool | None = Field(
            default=None,
            description="No color output flag from CLI (None = use Config value)",
        )

        @classmethod
        def _get_config_value(
            cls, config: FlextCliConfig, field_name: str
        ) -> FlextTypes.JsonValue | None:
            """Get config value for field if available."""
            if not hasattr(config, field_name):
                return None
            value: object = getattr(config, field_name)
            # Special handling for log_level (convert to string)
            if field_name == "log_level" and value is not None:
                return str(value)
            # Type narrowing: config values should be JsonValue compatible
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            if isinstance(value, dict):
                # dict[str, object] is compatible with JsonDict
                return value
            if isinstance(value, list):
                # list[object] is compatible with JsonValue
                return value
            # Convert to string for unknown types (ensures JsonValue compatibility)
            return str(value) if value is not None else None

        @classmethod
        def _fill_field_from_config(
            cls, result: dict[str, object], config: FlextCliConfig, field_name: str
        ) -> None:
            """Fill single field from config if None."""
            if result.get(field_name) is None:
                config_value = cls._get_config_value(config, field_name)
                if config_value is not None:
                    result[field_name] = config_value

        @model_validator(mode="before")
        @classmethod
        def fill_from_config_if_none(
            cls, data: dict[str, object] | object
        ) -> dict[str, object]:
            """Fill None values from Config (Config has priority over Constants).

            When fields are None, use values from FlextCliConfig.get_global_instance()
            if available. This ensures Config values are used instead of requiring
            explicit values to be passed.
            """
            if not isinstance(data, dict):
                # Convert non-dict to dict for Pydantic validation
                return {} if data is None else {"_data": data}

            # Try to get config instance (may not be available in all contexts)
            try:
                config = FlextCliConfig.get_global_instance()
            except Exception:
                # Config not available - return data as-is
                return data

            # Fill None values from config (Config has priority over Constants)
            result = dict(data)
            cls._fill_field_from_config(result, config, "verbose")
            cls._fill_field_from_config(result, config, "quiet")
            cls._fill_field_from_config(result, config, "debug")
            cls._fill_field_from_config(result, config, "trace")
            cls._fill_field_from_config(result, config, "log_level")
            # Special handling for log_format (maps to log_verbosity in config)
            if result.get("log_format") is None and hasattr(config, "log_verbosity"):
                result["log_format"] = config.log_verbosity
            cls._fill_field_from_config(result, config, "output_format")
            cls._fill_field_from_config(result, config, "no_color")

            return result

    # =========================================================================
    # AUTH MODELS - Pydantic 2 validation replacing manual checks
    # =========================================================================

    class TokenData(BaseModel):
        """Token data with Pydantic 2 validation - replaces manual validation.

        REFACTORED: Removed redundant validate_token_not_empty validator.
        StringConstraints(min_length=1, strip_whitespace=True) already ensures non-empty tokens.
        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        token: Annotated[
            str, StringConstraints(min_length=1, strip_whitespace=True)
        ] = Field(description="Authentication token")

    class PasswordAuth(BaseModel):
        """Password authentication with Pydantic 2 validation - replaces manual checks."""

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        username: Annotated[
            str,
            StringConstraints(
                min_length=FlextCliConstants.Auth.MIN_USERNAME_LENGTH,
                strip_whitespace=True,
            ),
        ] = Field(description="Username for authentication")

        password: Annotated[
            str,
            StringConstraints(
                min_length=FlextCliConstants.Auth.MIN_PASSWORD_LENGTH,
            ),
        ] = Field(description="Password for authentication")

    class CmdConfig(BaseModel):
        """CMD config with Pydantic 2 validation - replaces manual dict checks."""

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        host: str = Field(
            default=FlextCliConstants.NetworkDefaults.DEFAULT_HOST,
            description="Host address",
        )
        port: int = Field(
            default=FlextCliConstants.NetworkDefaults.DEFAULT_PORT,
            description="Port number",
            ge=1,
            le=65535,
        )
        timeout: int = Field(
            default=FlextCliConstants.TIMEOUTS.DEFAULT,
            description="Timeout in seconds",
            ge=0,
        )

    # System Information Models (replaces dict usage in debug.py)

    class SystemInfo(BaseModel):
        """System information model - replaces dict[str, FlextTypes.JsonValue].

        Pydantic 2 Features:
        - Explicit field types instead of generic JsonValue
        - Built-in validation
        - Type-safe serialization with model_dump()

        Usage:
            >>> info = FlextCliModels.SystemInfo(
            ...     python_version="3.13.0",
            ...     platform="Linux-6.17.1-x86_64",
            ...     architecture=["64bit", "ELF"],
            ...     processor="x86_64",
            ...     hostname="server01",
            ... )
            >>> info.model_dump()  # Pydantic 2 serialization
        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        python_version: str = Field(description="Python version string")
        platform: str = Field(description="Platform identifier")
        architecture: list[str] = Field(
            description="Architecture tuple as list [bits, linkage]"
        )
        processor: str = Field(description="Processor type")
        hostname: str = Field(description="System hostname")

    class EnvironmentInfo(BaseModel):
        """Environment variables model - replaces dict[str, str].

        Pydantic 2 Features:
        - Dict field with str constraints
        - Sensitive data masking handled in setter
        - Type-safe with proper validation

        Usage:
            >>> env = FlextCliModels.EnvironmentInfo(
            ...     variables={"PATH": "/usr/bin", "PASSWORD": "***MASKED***"}
            ... )
            >>> env.variables["PATH"]
            '/usr/bin'
        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        variables: dict[str, str] = Field(
            default_factory=dict, description="Environment variables (sensitive masked)"
        )

    class PathInfo(BaseModel):
        """Path information model - replaces dict[str, object].

        Pydantic 2 Features:
        - Explicit types instead of generic object
        - Path validation with Field
        - Type-safe access

        Usage:
            >>> path = FlextCliModels.PathInfo(
            ...     index=0, path="/usr/bin", exists=True, is_dir=True
            ... )
        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        index: int = Field(description="Path index in sys.path")
        path: str = Field(description="File system path")
        exists: bool = Field(description="Path exists")
        is_dir: bool = Field(description="Is directory")

    # Context and Prompts Models (replaces dict usage in context.py and prompts.py)

    class ContextExecutionResult(BaseModel):
        """Context execution result model - replaces dict in execute().

        Pydantic 2 Features:
        - Type-safe result instead of generic dict
        - Built-in validation for all fields
        - Immutable timestamp generation

        Usage:
            >>> result = FlextCliModels.ContextExecutionResult(
            ...     context_executed=True, command="test", arguments_count=2
            ... )
            >>> result.model_dump()  # Serializes to dict
        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        context_executed: bool = Field(description="Whether context was executed")
        command: str | None = Field(default=None, description="Command name (optional)")
        arguments_count: int = Field(ge=0, description="Number of arguments")
        timestamp: str = Field(
            default="",  # Will be set after import in __post_init__ or by caller
            description="ISO timestamp of execution",
        )

    class PromptStatistics(BaseModel):
        """Prompt statistics model - replaces dict in get_prompt_statistics().

        Pydantic 2 Features:
        - Type-safe statistics instead of generic dict
        - Automatic validation of counters (non-negative)
        - Clean API for accessing stats

        Usage:
            >>> stats = FlextCliModels.PromptStatistics(
            ...     prompts_executed=5,
            ...     interactive_mode=True,
            ...     default_timeout=30,
            ...     history_size=10,
            ... )
        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        prompts_executed: int = Field(ge=0, description="Total prompts executed")
        interactive_mode: bool = Field(description="Whether in interactive mode")
        default_timeout: int = Field(ge=0, description="Default timeout in seconds")
        history_size: int = Field(ge=0, description="Prompt history size")
        timestamp: str = Field(
            default="",  # Will be set by caller
            description="ISO timestamp",
        )

    # =========================================================================
    # CORE SERVICE MODELS - FlextCliCore service models
    # =========================================================================

    class CommandStatistics(BaseModel):
        """Command statistics model - replaces dict in get_command_statistics().

        Pydantic 2 Features:
            - Type-safe model instead of dict[str, JsonValue]
            - Automatic validation on creation
            - Clean serialization with model_dump()

        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        total_commands: int = Field(ge=0, description="Total registered commands")
        registered_commands: list[str] = Field(
            default_factory=list, description="List of registered command names"
        )
        status: bool = Field(description="Session active status")
        timestamp: str = Field(default="", description="ISO timestamp")

    class SessionStatistics(BaseModel):
        """Session statistics model - replaces dict in get_session_statistics().

        Pydantic 2 Features:
            - Type-safe model instead of dict[str, JsonValue]
            - Validates non-negative duration
            - Automatic field validation

        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        session_active: bool = Field(description="Whether session is active")
        session_duration_seconds: int = Field(
            ge=0, description="Session duration in seconds"
        )
        commands_available: int = Field(
            ge=0, description="Number of available commands"
        )
        configuration_loaded: bool = Field(
            description="Whether configuration is loaded"
        )
        session_config_keys: list[str] = Field(
            default_factory=list, description="Session configuration keys"
        )
        start_time: str = Field(description="Session start time (ISO or 'unknown')")
        current_time: str = Field(default="", description="Current time (ISO)")

    class ServiceExecutionResult(BaseModel):
        """Service execution result model - replaces dict in execute().

        Pydantic 2 Features:
            - Type-safe model instead of dict[str, JsonValue]
            - Validates service ready state
            - Clean structure for service execution

        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        service_executed: bool = Field(description="Whether service was executed")
        commands_count: int = Field(ge=0, description="Number of commands available")
        session_active: bool = Field(description="Whether session is active")
        execution_timestamp: str = Field(
            default="", description="Execution timestamp (ISO)"
        )
        service_ready: bool = Field(description="Whether service is ready")

    class CommandExecutionContextResult(BaseModel):
        """Command execution context result - replaces dict in execute_cli_command_with_context().

        Pydantic 2 Features:
            - Type-safe model instead of dict[str, JsonValue]
            - Supports optional user_id
            - Flexible context data

        """

        model_config = ConfigDict(frozen=False, validate_assignment=True)

        command: str = Field(description="Command name")
        status: bool = Field(description="Execution status")
        context: dict[str, FlextTypes.JsonValue] = Field(
            default_factory=dict, description="Context data"
        )
        timestamp: str = Field(default="", description="Execution timestamp (ISO)")
        user_id: str = Field(
            default=FlextCliConstants.CliSessionDefaults.DEFAULT_USER_ID,
            description="User ID (empty string if not provided)",
        )

    # =========================================================================
    # CONFIG SERVICE MODEL - Re-exported from _models_config to avoid circular imports
    # =========================================================================

    # Imported from _models_config to break circular dependency (config.py ↔ models.py)
    ConfigServiceExecutionResult = ConfigServiceExecutionResult


__all__ = [
    "FlextCliModels",
]
