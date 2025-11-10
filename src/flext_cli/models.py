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
from typing import Literal, Self, cast, get_args, get_origin

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
from pydantic_core import PydanticUndefined

from flext_cli.constants import FlextCliConstants
from flext_cli.mixins import FlextCliMixins
from flext_cli.typings import FlextCliTypes

logger = FlextLogger(__name__)


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
        """Click option specification model - replaces FlextTypes.JsonDict in Click option generation.

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
                FlextResult containing CLI parameter specification FlextTypes.JsonDict with:
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
                    return FlextResult["FlextCliModels.CliParameterSpec"].fail(
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

                return FlextResult["FlextCliModels.CliParameterSpec"].ok(cli_param)
            except Exception as e:
                return FlextResult["FlextCliModels.CliParameterSpec"].fail(
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

                return FlextResult[list["FlextCliModels.CliParameterSpec"]].ok(
                    cli_params
                )
            except Exception as e:
                return FlextResult[list["FlextCliModels.CliParameterSpec"]].fail(
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
                    return FlextResult[list["FlextCliModels.CliOptionSpec"]].fail(
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

                return FlextResult[list["FlextCliModels.CliOptionSpec"]].ok(
                    click_options
                )
            except Exception as e:
                return FlextResult[list["FlextCliModels.CliOptionSpec"]].fail(
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

        def _build_parameters(self) -> None:
            """Build parameter definitions from model fields."""
            for field_name, field_info in self.model_class.model_fields.items():
                param_name = field_name.replace("_", "-")
                self.field_mapping[param_name] = field_name

                # Get field type and format it
                field_type = field_info.annotation or str
                type_str = self._format_type_annotation(field_type)

                # Build typer.Option specification
                default_value = self._get_field_default(field_name, field_info)
                is_required = field_info.is_required()
                help_text = field_info.description or ""

                # Generate parameter definition
                if is_required:
                    self.params_def.append(
                        f"{param_name}: {type_str} = typer.Option(..., help={help_text!r})"
                    )
                else:
                    self.params_def.append(
                        f"{param_name}: {type_str} = typer.Option({default_value!r}, help={help_text!r})"
                    )

                self.params_call.append(f"{field_name}={param_name}")

        @staticmethod
        def _format_type_annotation(annotation: object) -> str:
            """Format type annotation for CLI help text.

            Args:
                annotation: Type annotation to format

            Returns:
                str: Human-readable type string

            """
            if annotation is None:
                return "Any"
            if hasattr(annotation, "__name__"):
                return str(annotation.__name__)
            return str(annotation)

        def _get_field_default(
            self, field_name: str, field_info: fields.FieldInfo
        ) -> FlextTypes.JsonValue:
            """Get default value for field.

            Args:
                field_name: Name of the field
                field_info: Pydantic FieldInfo

            Returns:
                Default value

            """
            # Check config first
            if self.config is not None and hasattr(self.config, field_name):
                value = getattr(self.config, field_name)
                # Validate it's JSON-compatible
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    return value
                return str(value)

            # Use field default
            if field_info.default is not PydanticUndefined:
                default = field_info.default
                if isinstance(default, (str, int, float, bool, list, dict, type(None))):
                    return default
                return str(default)

            if field_info.default_factory is not None and callable(
                field_info.default_factory
            ):
                try:
                    # Call factory - may raise if it requires arguments
                    factory_func = field_info.default_factory
                    if callable(factory_func):
                        # Type safety: factory is callable and may require no args
                        factory_result = factory_func()  # type: ignore[call-arg]
                    if isinstance(
                        factory_result, (str, int, float, bool, list, dict, type(None))
                    ):
                        return factory_result
                    return str(factory_result)
                except TypeError:
                    # Factory requires arguments we don't have
                    return None

            return None

        def _generate_function(self) -> Callable[..., None]:
            """Generate the command function dynamically using closure pattern.

            Creates a function with explicit named parameters for Click/Typer compatibility.
            Uses __signature__ to assign the correct signature without exec.

            Returns:
                Generated function

            """
            # Capture model_class and handler in closure
            model_class = self.model_class
            handler = self.handler
            field_mapping = self.field_mapping

            def generated_command(**kwargs: FlextTypes.JsonValue) -> None:
                """Dynamically generated command function.

                Uses closure to capture model_class, handler, and field_mapping
                without requiring exec or eval.
                """
                # Build model arguments from CLI kwargs
                model_args: FlextTypes.JsonDict = {}
                for cli_param, field_name in field_mapping.items():
                    if cli_param in kwargs:
                        model_args[field_name] = kwargs[cli_param]

                # Create model instance and call handler
                model_instance = model_class(**model_args)
                handler(model_instance)

            # Build explicit signature for Click/Typer introspection
            parameters = []
            # Use .values() since we only need field_name, not cli_param
            for field_name in field_mapping.values():
                field_info = self.model_class.model_fields.get(field_name)
                if field_info:
                    default_value = self._get_field_default(field_name, field_info)
                    # Create Parameter with field_name (underscores) not cli_param (hyphens)
                    # Python identifiers can't have hyphens
                    param = inspect.Parameter(
                        field_name,  # Use field_name with underscores, not cli_param with hyphens
                        inspect.Parameter.KEYWORD_ONLY,
                        default=default_value
                        if default_value is not None
                        else inspect.Parameter.empty,
                        annotation=field_info.annotation,
                    )
                    parameters.append(param)

            # Assign signature to function for Click/Typer introspection
            # Type safety: __signature__ is a valid runtime attribute for callables
            generated_command.__signature__ = inspect.Signature(parameters)  # type: ignore[attr-defined]

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
                    for cli_param, field_name in self.field_mapping.items():
                        cli_value = kwargs.get(cli_param)
                        if cli_value is not None:
                            setattr(self.config, field_name, cli_value)

                func(**kwargs)

            # Preserve signature from wrapped function for Click/Typer introspection
            if hasattr(func, "__signature__"):
                # Type safety: __signature__ is a valid runtime attribute for callables
                wrapped.__signature__ = func.__signature__  # type: ignore[attr-defined]

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

            # Import here to avoid circular dependency
            from flext_cli.config import FlextCliConfig

            # Get field metadata
            self.fields = FlextCliConfig.model_fields
            self.schema = FlextCliConfig.model_json_schema()

            if field_name not in self.fields:
                msg = f"Field {field_name!r} not found in FlextCliConfig"
                raise ValueError(msg)

            self.field_info = self.fields[field_name]
            self.field_schema = self.schema["properties"].get(field_name, {})
            self.param_meta = registry.get(field_name, {})

        def build(self) -> OptionInfo:
            """Build typer.Option from field metadata.

            Returns:
                typer.Option instance

            """
            import typer  # Local import for nested class access

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

            return cast(
                "OptionInfo",
                typer.Option(
                    default_value,
                    *param_decls,
                    help=help_text,
                    case_sensitive=case_sensitive,
                    min=min_constraint,
                    max=max_constraint,
                    show_default=default_value is not None,
                ),
            )

        def _extract_type(self) -> type | types.UnionType:
            """Extract base type from field annotation."""
            field_type = normalize_annotation(self.field_info.annotation)

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
            cls, data: FlextTypes.JsonValue
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

            # Type narrowing: data is dict[str, JsonValue] after isinstance check

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
            # Type safety: dict values from data.items() are JSON-compatible
            normalized_data: FlextCliTypes.Data.CliDataDict = {
                "command": command,
                "execution_time": data.get("execution_time"),  # type: ignore[dict-item]
                **{k: v for k, v in data.items() if k != "command"},  # type: ignore[misc]
            }

            # Return normalized data (type is already correct)
            return FlextResult[FlextCliTypes.Data.CliCommandData | None].ok(
                normalized_data
            )

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate command business rules using Pydantic v2 patterns."""
            # Inline validation: command_line must not be empty
            if not self.command_line or not str(self.command_line).strip():
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                        field_name="Command line"
                    )
                )

            # Inline validation: status must be valid
            if self.status not in FlextCliConstants.COMMAND_STATUSES_LIST:
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                        field_name="status",
                        valid_values=FlextCliConstants.COMMAND_STATUSES_LIST,
                    )
                )

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

            return self

        @field_serializer("commands")
        def serialize_commands(
            self, value: list[FlextCliModels.CliCommand], _info: typing.Any
        ) -> list[FlextTypes.JsonDict]:
            """Serialize commands with summary information."""
            return [
                {
                    "id": str(cmd.id) if hasattr(cmd, "id") else "",
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
            """Validate session business rules using Pydantic v2 patterns."""
            # Inline validation: session_id must not be empty
            if not self.session_id or not str(self.session_id).strip():
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                        field_name=FlextCliConstants.ModelsFieldNames.SESSION_ID
                    )
                )

            # Validate user_id if provided
            if self.user_id is not None and not self.user_id.strip():
                return FlextResult[None].fail(
                    FlextCliConstants.ModelsErrorMessages.USER_ID_EMPTY
                )

            # Inline validation: status must be valid
            if self.status not in FlextCliConstants.SESSION_STATUSES_LIST:
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                        field_name=FlextCliConstants.ModelsFieldNames.STATUS,
                        valid_values=FlextCliConstants.SESSION_STATUSES_LIST,
                    )
                )

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

    class DebugInfo(FlextModels.ArbitraryTypesModel):
        """Debug information model with comprehensive diagnostic data.

        Extends FlextModels.ArbitraryTypesModel for strict validation.

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
            """Validate debug info business rules using Pydantic v2 patterns."""
            # Inline validation: service must not be empty
            if not self.service or not str(self.service).strip():
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.FIELD_CANNOT_BE_EMPTY.format(
                        field_name="Service name"
                    )
                )

            # Inline validation: level must be valid
            if self.level not in FlextCliConstants.DEBUG_LEVELS_LIST:
                return FlextResult[None].fail(
                    FlextCliConstants.MixinsValidationMessages.INVALID_ENUM_VALUE.format(
                        field_name="level",
                        valid_values=FlextCliConstants.DEBUG_LEVELS_LIST,
                    )
                )

            return FlextResult[None].ok(None)

    class LoggingConfig(FlextModels.ArbitraryTypesModel):
        """Logging configuration model for CLI operations.

        Extends FlextModels.ArbitraryTypesModel for flexible configuration.

        Pydantic 2.11 Features:
        - Annotated fields with rich metadata
        - computed_field for derived properties
        - field_validator for business logic validation
        """

        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
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


__all__ = [
    "FlextCliModels",
]
