"""FLEXT CLI Context - CLI execution context management.

Provides CLI execution context with type-safe operations and FlextResult patterns.
Follows FLEXT standards with single FlextCliContext class per module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCore, FlextResult
from pydantic import BaseModel

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels
from flext_cli.typings import FlextCliTypes


class FlextCliContext(FlextCore.Service[FlextCliTypes.Data.CliDataDict]):
    """CLI execution context management service.

    Provides type-safe CLI context operations with FlextResult railway patterns.
    Wraps CliContext model from FlextCliModels for service-level operations.
    """

    def __init__(self, **data: object) -> None:
        """Initialize CLI context service with Phase 1 context enrichment."""
        super().__init__(**data)
        # Logger and container inherited from FlextCore.Service via FlextMixins
        self._model_class = FlextCliModels.CliContext

    def create_context(
        self,
        command: str | None = None,
        arguments: FlextCore.Types.StringList | None = None,
        environment_variables: FlextCliTypes.Data.CliConfigData | None = None,
        working_directory: str | None = None,
        **data: object,
    ) -> FlextResult[FlextCliModels.CliContext]:
        """Create a new CLI context instance.

        Args:
            command: CLI command to execute
            arguments: Command arguments
            environment_variables: Environment variables
            working_directory: Working directory
            **data: Additional context data

        Returns:
            FlextResult[FlextCliModels.CliContext]: Created context instance

        """
        try:
            context = self._model_class(
                command=command,
                arguments=arguments,
                environment_variables=environment_variables,
                working_directory=working_directory,
                **data,
            )
            return FlextResult[FlextCliModels.CliContext].ok(context)
        except Exception as e:
            return FlextResult[FlextCliModels.CliContext].fail(
                f"Failed to create context: {e}"
            )

    def validate_context(
        self,
        context: FlextCliModels.CliContext,
    ) -> FlextResult[None]:
        """Validate CLI context instance.

        Args:
            context: Context to validate

        Returns:
            FlextResult[None]: Validation result

        """
        try:
            # Validation is automatic via Pydantic in the model
            # This method provides explicit validation interface
            if not context.command and not context.arguments:
                return FlextResult[None].fail(
                    "Context must have either command or arguments"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.CONTEXT_VALIDATION_FAILED.format(
                    error=e
                )
            )

    # ========================================================================
    # MODEL CONTEXT PROPAGATION - Attach/retrieve models from context
    # ========================================================================

    def create_context_from_model(
        self,
        model: BaseModel,
        command: str | None = None,
    ) -> FlextResult[FlextCliModels.CliContext]:
        """Create CLI context from Pydantic model instance.

        Args:
            model: Pydantic model instance to attach to context
            command: Optional command name

        Returns:
            FlextResult[FlextCliModels.CliContext]: Context with attached model

        """
        try:
            # Convert model to dict for context metadata
            model_data = model.model_dump()

            # Create context
            context = self._model_class(
                command=command,
                arguments=[],
                environment_variables={},
                working_directory=None,
            )

            # Attach model data to context metadata
            for key, value in model_data.items():
                set_result = context.set_metadata(f"model_{key}", value)
                if set_result.is_failure:
                    return FlextResult[FlextCliModels.CliContext].fail(
                        f"Failed to attach model data: {set_result.error}"
                    )

            # Store model class name
            model_class_result = context.set_metadata(
                "model_class", model.__class__.__name__
            )
            if model_class_result.is_failure:
                return FlextResult[FlextCliModels.CliContext].fail(
                    f"Failed to store model class: {model_class_result.error}"
                )

            return FlextResult[FlextCliModels.CliContext].ok(context)
        except Exception as e:
            return FlextResult[FlextCliModels.CliContext].fail(
                f"Context creation from model failed: {e}"
            )

    def attach_model_to_context(
        self,
        context: FlextCliModels.CliContext,
        model: BaseModel,
        prefix: str = "model",
    ) -> FlextResult[None]:
        """Attach Pydantic model instance to existing context.

        Args:
            context: CLI context to attach model to
            model: Pydantic model instance
            prefix: Prefix for model data keys in context metadata

        Returns:
            FlextResult[None]: Success or error

        """
        try:
            # Convert model to dict
            model_data = model.model_dump()

            # Attach each field to context metadata
            for key, value in model_data.items():
                metadata_key = f"{prefix}_{key}"
                set_result = context.set_metadata(metadata_key, value)
                if set_result.is_failure:
                    return FlextResult[None].fail(
                        f"Failed to attach {key}: {set_result.error}"
                    )

            # Store model class information
            class_result = context.set_metadata(
                f"{prefix}_class", model.__class__.__name__
            )
            if class_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to store model class: {class_result.error}"
                )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(
                FlextCliConstants.ErrorMessages.MODEL_ATTACHMENT_FAILED.format(error=e)
            )

    def extract_model_from_context(
        self,
        context: FlextCliModels.CliContext,
        model_class: type[BaseModel],
        prefix: str = "model",
    ) -> FlextResult[BaseModel]:
        """Extract Pydantic model instance from context metadata.

        Args:
            context: CLI context containing model data
            model_class: Pydantic model class to instantiate
            prefix: Prefix used when attaching model data

        Returns:
            FlextResult[BaseModel]: Reconstructed model instance or error

        """
        try:
            # Extract model fields from context metadata
            model_data: dict[str, object] = {}

            # Get all model fields
            for field_name in model_class.model_fields:
                metadata_key = f"{prefix}_{field_name}"
                field_result = context.get_metadata(metadata_key)

                if field_result.is_success:
                    model_data[field_name] = field_result.unwrap()

            # Reconstruct model from extracted data
            model_instance = model_class(**model_data)

            return FlextResult[BaseModel].ok(model_instance)
        except Exception as e:
            return FlextResult[BaseModel].fail(
                FlextCliConstants.ErrorMessages.MODEL_EXTRACTION_FAILED.format(error=e)
            )

    def get_model_metadata(
        self,
        context: FlextCliModels.CliContext,
        prefix: str = "model",
    ) -> FlextResult[dict[str, object]]:
        """Get all model-related metadata from context.

        Args:
            context: CLI context
            prefix: Prefix for model data keys

        Returns:
            FlextResult containing dictionary of model metadata

        """
        try:
            # Get context summary to access metadata
            summary_result = context.get_context_summary()
            if summary_result.is_failure:
                return FlextResult[dict[str, object]].fail(
                    f"Failed to get context summary: {summary_result.error}"
                )

            summary = summary_result.unwrap()
            metadata_keys = summary.get("metadata_keys", [])

            # Filter for model-prefixed keys
            model_metadata: dict[str, object] = {}

            # Ensure metadata_keys is a list before iterating
            if isinstance(metadata_keys, list):
                for key in metadata_keys:
                    if isinstance(key, str) and key.startswith(f"{prefix}_"):
                        value_result = context.get_metadata(key)
                        if value_result.is_success:
                            # Remove prefix from key for cleaner output
                            clean_key = key[len(f"{prefix}_") :]
                            model_metadata[clean_key] = value_result.unwrap()

            return FlextResult[dict[str, object]].ok(model_metadata)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(
                f"Metadata retrieval failed: {e}"
            )

    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute context service operations.

        Returns:
            FlextResult[FlextCliTypes.Data.CliDataDict]: Service execution result

        """
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "service": "FlextCliContext",
            "status": "operational",
        })


__all__ = [
    "FlextCliContext",
]
