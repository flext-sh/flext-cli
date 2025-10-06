"""FLEXT CLI Processors - Single unified class following FLEXT standards.

Provides CLI-specific processor implementations using flext-core patterns.
Single FlextCliProcessors class with nested processor subclasses following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any, override

from flext_core import FlextResult, FlextService, FlextTypes
from pydantic import BaseModel

from flext_cli.models import FlextCliModels


class FlextCliProcessors(FlextService[FlextTypes.Dict]):
    """Single unified CLI processors class following FLEXT standards.

    Contains all processor implementations for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested subclasses.

    ARCHITECTURAL COMPLIANCE:
    - Inherits from FlextProcessors to reuse processor patterns and pipeline functionality
    - Uses centralized processor patterns from FlextProcessors
    - Implements CLI-specific extensions while reusing core functionality
    - Provides execute() and execute() for CLI processor operations
    """

    @override
    def __init__(self) -> None:
        """Initialize CLI processors service with FlextProcessors base."""
        super().__init__()
        self._command_processor = self.CommandProcessor()

    def execute(self) -> FlextResult[FlextTypes.Dict]:
        """Execute processors service operation.

        Provides CLI-specific processor execution status.
        """
        return FlextResult[FlextTypes.Dict].ok({
            "status": "operational",
            "service": "flext-cli-processors",
            "timestamp": "2025-01-08T00:00:00Z",
            "version": "2.0.0",
            "processors": ["CommandProcessor", "ModelProcessor"],
        })

    # ========================================================================
    # MODEL VALIDATION BRIDGE - Process and validate data with Pydantic models
    # ========================================================================

    class ModelProcessor:
        """Processor for validating and transforming data using Pydantic models.

        Provides model-driven data validation and processing pipeline integration.

        ARCHITECTURAL PATTERN:
        - Validate CLI data with Pydantic models
        - Transform validated data for CLI operations
        - Create processing pipelines from model chains
        - Integrate validation into CLI data flow

        USAGE:
            processor = ModelProcessor()
            result = processor.validate_and_process(data, ConfigModel)
            # Data is validated and ready for CLI operations
        """

        @override
        def __init__(self) -> None:
            """Initialize model processor."""
            self._processed_models: list[BaseModel] = []
            self._validation_errors: list[str] = []

        def validate_with_model(
            self, data: dict[str, Any], model_class: type[BaseModel]
        ) -> FlextResult[BaseModel]:
            """Validate data using Pydantic model.

            Args:
                data: Data dictionary to validate
                model_class: Pydantic model class for validation

            Returns:
                FlextResult containing validated model instance or error

            """
            validation_result = (
                FlextCliModels.CliModelConverter.validate_cli_data_with_model(
                    model_class, data
                )
            )

            if validation_result.is_success:
                validated_model = validation_result.unwrap()
                self._processed_models.append(validated_model)
                return FlextResult[BaseModel].ok(validated_model)

            error = validation_result.error or "Validation failed"
            self._validation_errors.append(error)
            return FlextResult[BaseModel].fail(error)

        def validate_and_process(
            self, data: dict[str, Any], model_class: type[BaseModel]
        ) -> FlextResult[dict[str, Any]]:
            """Validate data with model and return processed dict.

            Args:
                data: Input data dictionary
                model_class: Pydantic model class for validation

            Returns:
                FlextResult containing validated and processed data dictionary

            """
            # Validate with model
            validation_result = self.validate_with_model(data, model_class)

            if validation_result.is_failure:
                return FlextResult[dict[str, Any]].fail(
                    f"Validation failed: {validation_result.error}"
                )

            validated_model = validation_result.unwrap()

            # Convert back to dict for CLI processing
            processed_data = validated_model.model_dump()

            return FlextResult[dict[str, Any]].ok(processed_data)

        def create_model_pipeline(
            self, *model_classes: type[BaseModel]
        ) -> FlextResult[list[type[BaseModel]]]:
            """Create processing pipeline from multiple models.

            Args:
                *model_classes: Sequence of Pydantic model classes

            Returns:
                FlextResult containing ordered list of model classes

            """
            try:
                if not model_classes:
                    return FlextResult[list[type[BaseModel]]].fail(
                        "At least one model class required"
                    )

                pipeline: list[type[BaseModel]] = list(model_classes)
                return FlextResult[list[type[BaseModel]]].ok(pipeline)
            except Exception as e:
                return FlextResult[list[type[BaseModel]]].fail(
                    f"Pipeline creation failed: {e}"
                )

        def process_through_pipeline(
            self, data: dict[str, Any], pipeline: list[type[BaseModel]]
        ) -> FlextResult[dict[str, Any]]:
            """Process data through sequence of model validations.

            Args:
                data: Input data
                pipeline: List of model classes to validate against

            Returns:
                FlextResult containing data validated by all models

            """
            try:
                current_data = data.copy()

                for model_class in pipeline:
                    # Validate with current model
                    result = self.validate_and_process(current_data, model_class)

                    if result.is_failure:
                        return FlextResult[dict[str, Any]].fail(
                            f"Pipeline failed at {model_class.__name__}: {result.error}"
                        )

                    # Update data with validated output
                    current_data = result.unwrap()

                return FlextResult[dict[str, Any]].ok(current_data)
            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"Pipeline processing failed: {e}"
                )

        def get_processed_models(self) -> FlextResult[list[BaseModel]]:
            """Get all successfully processed models.

            Returns:
                FlextResult containing list of processed model instances

            """
            try:
                return FlextResult[list[BaseModel]].ok(self._processed_models.copy())
            except Exception as e:
                return FlextResult[list[BaseModel]].fail(
                    f"Failed to get processed models: {e}"
                )

        def get_validation_errors(self) -> FlextResult[list[str]]:
            """Get all validation errors encountered.

            Returns:
                FlextResult containing list of validation error messages

            """
            try:
                return FlextResult[list[str]].ok(self._validation_errors.copy())
            except Exception as e:
                return FlextResult[list[str]].fail(
                    f"Failed to get validation errors: {e}"
                )

        def clear_history(self) -> FlextResult[None]:
            """Clear processing history and errors.

            Returns:
                FlextResult indicating success or failure

            """
            try:
                self._processed_models.clear()
                self._validation_errors.clear()
                return FlextResult[None].ok(None)
            except Exception as e:
                return FlextResult[None].fail(f"Failed to clear history: {e}")

    class CommandProcessor:
        """CLI command processor for processing command operations."""

        @override
        def __init__(self) -> None:
            """Initialize command processor."""
            self._processed_commands: list[FlextCliModels.CliCommand] = []

        def process_command(
            self, command: FlextCliModels.CliCommand
        ) -> FlextResult[FlextCliModels.CliCommand]:
            """Process a CLI command.

            Args:
                command: Command to process

            Returns:
                FlextResult[FlextCliModels.CliCommand]: Processed command or error

            """
            try:
                # Validate command business rules
                validation_result = command.validate_business_rules()
                if not validation_result.is_success:
                    return FlextResult[FlextCliModels.CliCommand].fail(
                        validation_result.error or "Command validation failed"
                    )

                # Process the command
                command.update_timestamp()
                self._processed_commands.append(command)

                return FlextResult[FlextCliModels.CliCommand].ok(command)
            except Exception as e:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command processing failed: {e}"
                )

        def get_processed_commands(
            self,
        ) -> FlextResult[list[FlextCliModels.CliCommand]]:
            """Get all processed commands.

            Returns:
                FlextResult[list[FlextCliModels.CliCommand]]: List of processed commands or error

            """
            try:
                return FlextResult[list[FlextCliModels.CliCommand]].ok(
                    self._processed_commands.copy()
                )
            except Exception as e:
                return FlextResult[list[FlextCliModels.CliCommand]].fail(
                    f"Failed to get processed commands: {e}"
                )

        def clear_processed_commands(self) -> FlextResult[int]:
            """Clear all processed commands.

            Returns:
                FlextResult[int]: Number of commands cleared or error

            """
            try:
                count = len(self._processed_commands)
                self._processed_commands.clear()
                return FlextResult[int].ok(count)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to clear processed commands: {e}")

    class SessionProcessor:
        """CLI session processor for processing session operations."""

        @override
        def __init__(self) -> None:
            """Initialize session processor."""
            self._processed_sessions: list[FlextCliModels.CliSession] = []

        def process_session(
            self, session: FlextCliModels.CliSession
        ) -> FlextResult[FlextCliModels.CliSession]:
            """Process a CLI session.

            Args:
                session: Session to process

            Returns:
                FlextResult[FlextCliModels.CliSession]: Processed session or error

            """
            try:
                # Validate session business rules
                validation_result = session.validate_business_rules()
                if not validation_result.is_success:
                    return FlextResult[FlextCliModels.CliSession].fail(
                        validation_result.error or "Session validation failed"
                    )

                # Process the session
                session.update_timestamp()
                self._processed_sessions.append(session)

                return FlextResult[FlextCliModels.CliSession].ok(session)
            except Exception as e:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session processing failed: {e}"
                )

        def get_processed_sessions(
            self,
        ) -> FlextResult[list[FlextCliModels.CliSession]]:
            """Get all processed sessions.

            Returns:
                FlextResult[list[FlextCliModels.CliSession]]: List of processed sessions or error

            """
            try:
                return FlextResult[list[FlextCliModels.CliSession]].ok(
                    self._processed_sessions.copy()
                )
            except Exception as e:
                return FlextResult[list[FlextCliModels.CliSession]].fail(
                    f"Failed to get processed sessions: {e}"
                )

        def clear_processed_sessions(self) -> FlextResult[int]:
            """Clear all processed sessions.

            Returns:
                FlextResult[int]: Number of sessions cleared or error

            """
            try:
                count = len(self._processed_sessions)
                self._processed_sessions.clear()
                return FlextResult[int].ok(count)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to clear processed sessions: {e}")

    class DataProcessor:
        """CLI data processor for processing data operations."""

        @override
        def __init__(self) -> None:
            """Initialize data processor."""
            self._processed_data: FlextTypes.List = []

        def _transform_data(self, data: object) -> object:
            """Transform data for processing.

            Args:
                data: Raw data to transform

            Returns:
                object: Transformed data

            """
            # Basic transformation - could be extended with more complex logic
            if isinstance(data, dict):
                # Add processing metadata to dictionary data
                transformed_data = data.copy()
                if isinstance(transformed_data, dict):
                    transformed_data["_processed"] = True
                return transformed_data
            if isinstance(data, (list, tuple)):
                # Process list/tuple data
                return list(data) if not isinstance(data, list) else data
            # Return data as-is for other types
            return data

        def process_data(self, data: object) -> FlextResult[object]:
            """Process data.

            Args:
                data: Data to process

            Returns:
                FlextResult[object]: Processed data or error

            """
            try:
                # Basic data processing
                if data is None:
                    return FlextResult[object].fail("Data cannot be None")

                # Process the data with proper transformation
                processed = self._transform_data(data)
                self._processed_data.append(processed)

                return FlextResult[object].ok(processed)
            except Exception as e:
                return FlextResult[object].fail(f"Data processing failed: {e}")

        def get_processed_data(self) -> FlextResult[FlextTypes.List]:
            """Get all processed data.

            Returns:
                FlextResult[FlextTypes.List]: List of processed data or error

            """
            try:
                return FlextResult[FlextTypes.List].ok(self._processed_data.copy())
            except Exception as e:
                return FlextResult[FlextTypes.List].fail(
                    f"Failed to get processed data: {e}"
                )

        def clear_processed_data(self) -> FlextResult[int]:
            """Clear all processed data.

            Returns:
                FlextResult[int]: Number of data items cleared or error

            """
            try:
                count = len(self._processed_data)
                self._processed_data.clear()
                return FlextResult[int].ok(count)
            except Exception as e:
                return FlextResult[int].fail(f"Failed to clear processed data: {e}")


__all__ = [
    "FlextCliProcessors",
]
