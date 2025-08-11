"""FLEXT CLI Legacy Compatibility Module - Backward Compatibility Bridge.

This module provides backward compatibility shims for deprecated flext-cli classes
and functions that have been refactored to use flext-core patterns. Includes
deprecation warnings to guide users toward the new recommended patterns.

Legacy Components:
    - LegacyFlextFactory: Deprecated factory (use FlextEntityFactory from flext-core)
    - CLIEntityFactory: Deprecated CLI-specific factory (use direct instantiation)
    - Legacy decorators: Deprecated decorators (use flext-core decorators)
    - Legacy mixins: Deprecated mixins (use flext-core mixins)

Architecture:
    - Facade Pattern: Provides same interface while delegating to new implementations
    - Deprecation Warnings: Clear migration path for users
    - Feature Parity: Maintains exact same API while using modern implementations
    - Gradual Migration: Allows incremental adoption of new patterns

Deprecation Timeline:
    - Version 2.0.0: Legacy module introduced with warnings
    - Version 2.1.0: Legacy warnings become more prominent
    - Version 3.0.0: Legacy module will be removed entirely

Usage (Deprecated - For Backward Compatibility Only):
    Legacy factory usage:
    >>> from flext_cli.legacy import LegacyFlextFactory
    >>> factory = LegacyFlextFactory()  # Issues deprecation warning
    >>> entity = factory.create_entity(data)

    NEW RECOMMENDED USAGE:
    >>> from flext_core import FlextEntityFactory
    >>> from flext_cli.domain.entities import CLICommand
    >>> command = CLICommand(name="test", command_line="echo hello")

Migration Guide:
    1. Replace `from flext_cli.legacy import LegacyFlextFactory` 
       with `from flext_core import FlextEntityFactory`
    2. Replace factory.create_entity() calls with direct instantiation
    3. Update imports to use flext_core root module only
    4. Remove dependency on legacy module entirely

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import warnings
from typing import Any, TypeVar

# REFACTORED: Import ONLY from flext_core root module - NO submodule imports
from flext_core import (
    FlextEntity,
    FlextEntityFactory,
    FlextResult,
)

T = TypeVar("T", bound=FlextEntity)

# Legacy deprecation warning helper
def _issue_legacy_warning(old_name: str, new_recommendation: str) -> None:
    """Issue standardized deprecation warning for legacy components."""
    warnings.warn(
        f"{old_name} is deprecated and will be removed in flext-cli v3.0.0. "
        f"Use {new_recommendation} instead. "
        "See flext-cli migration guide for details.",
        DeprecationWarning,
        stacklevel=3,
    )


class LegacyFlextFactory:
    """Deprecated legacy factory - use FlextEntityFactory from flext-core instead.
    
    DEPRECATED: This class is deprecated as of flext-cli v2.0.0 and will be
    removed in v3.0.0. Use FlextEntityFactory from flext-core directly.
    
    Migration:
        OLD: LegacyFlextFactory().create_entity(data)
        NEW: Direct instantiation - CLICommand(name="test", command_line="echo hello")
    """

    def __init__(self) -> None:
        """Initialize legacy factory with deprecation warning."""
        _issue_legacy_warning(
            "LegacyFlextFactory",
            "direct entity instantiation or FlextEntityFactory from flext-core"
        )
        self._core_factory = FlextEntityFactory()

    def create_entity(self, entity_type: type[T], data: dict[str, Any]) -> T:
        """Create entity using legacy interface.
        
        DEPRECATED: Use direct instantiation instead.
        
        Args:
            entity_type: Type of entity to create
            data: Entity data dictionary
            
        Returns:
            Created entity instance

        """
        _issue_legacy_warning(
            "LegacyFlextFactory.create_entity()",
            f"{entity_type.__name__}(**data) direct instantiation"
        )

        # Delegate to direct instantiation since that's the new pattern
        return entity_type(**data)

    def validate_entity(self, entity: FlextEntity) -> FlextResult[None]:
        """Validate entity using legacy interface.
        
        DEPRECATED: Use entity.validate_business_rules() directly.
        
        Args:
            entity: Entity to validate
            
        Returns:
            FlextResult indicating validation success or failure

        """
        _issue_legacy_warning(
            "LegacyFlextFactory.validate_entity()",
            "entity.validate_business_rules() direct method call"
        )

        return entity.validate_business_rules()


class CLIEntityFactory:
    """Deprecated CLI-specific entity factory.
    
    DEPRECATED: This class is deprecated as of flext-cli v2.0.0 and will be
    removed in v3.0.0. Use direct instantiation of CLI entities instead.
    
    Migration:
        OLD: CLIEntityFactory().create_command(name, command_line)
        NEW: CLICommand(id=str(uuid4()), name=name, command_line=command_line)
    """

    def __init__(self) -> None:
        """Initialize CLI factory with deprecation warning."""
        _issue_legacy_warning(
            "CLIEntityFactory",
            "direct CLI entity instantiation with uuid.uuid4() for IDs"
        )

    def create_command(self, name: str, command_line: str, **kwargs: Any) -> Any:
        """Create CLI command using legacy interface.
        
        DEPRECATED: Import CLICommand and use direct instantiation.
        
        Args:
            name: Command name
            command_line: Command line string
            **kwargs: Additional command attributes
            
        Returns:
            CLICommand instance

        """
        # Import here to avoid circular imports
        import uuid

        from flext_cli.domain.entities import CLICommand, CommandType

        _issue_legacy_warning(
            "CLIEntityFactory.create_command()",
            "CLICommand(id=str(uuid.uuid4()), name=name, command_line=command_line)"
        )

        # Extract command type with backward compatibility
        command_type = kwargs.get("command_type", CommandType.CLI)
        if isinstance(command_type, str):
            command_type = CommandType.CLI if command_type == "cli" else CommandType.SYSTEM

        return CLICommand(
            id=str(uuid.uuid4()),
            name=name,
            command_line=command_line,
            command_type=command_type,
            **{k: v for k, v in kwargs.items() if k != "command_type"}
        )

    def create_session(self, session_id: str, **kwargs: Any) -> Any:
        """Create CLI session using legacy interface.
        
        DEPRECATED: Import CLISession and use direct instantiation.
        
        Args:
            session_id: Session identifier
            **kwargs: Additional session attributes
            
        Returns:
            CLISession instance

        """
        # Import here to avoid circular imports
        import uuid

        from flext_cli.domain.entities import CLISession

        _issue_legacy_warning(
            "CLIEntityFactory.create_session()",
            "CLISession(id=str(uuid.uuid4()), session_id=session_id)"
        )

        return CLISession(
            id=str(uuid.uuid4()),
            session_id=session_id,
            **kwargs
        )

    def create_plugin(self, name: str, version: str = "1.0.0", **kwargs: Any) -> Any:
        """Create CLI plugin using legacy interface.
        
        DEPRECATED: Import CLIPlugin and use direct instantiation.
        
        Args:
            name: Plugin name
            version: Plugin version
            **kwargs: Additional plugin attributes
            
        Returns:
            CLIPlugin instance

        """
        # Import here to avoid circular imports
        import uuid

        from flext_cli.domain.entities import CLIPlugin

        _issue_legacy_warning(
            "CLIEntityFactory.create_plugin()",
            "CLIPlugin(id=str(uuid.uuid4()), name=name, version=version)"
        )

        return CLIPlugin(
            id=str(uuid.uuid4()),
            name=name,
            version=version,
            **kwargs
        )


# Legacy decorator shims
def legacy_validate_result(func: Any) -> Any:
    """Deprecated result validation decorator.
    
    DEPRECATED: Use @FlextDecorators.validate_result from flext-core instead.
    """
    _issue_legacy_warning(
        "@legacy_validate_result",
        "@FlextDecorators.validate_result from flext_core"
    )

    # Import here to avoid circular imports
    from flext_core import FlextDecorators

    return FlextDecorators.validate_result(func)


def legacy_handle_errors(func: Any) -> Any:
    """Deprecated error handling decorator.
    
    DEPRECATED: Use @FlextErrorHandlingDecorators.handle_errors from flext-core.
    """
    _issue_legacy_warning(
        "@legacy_handle_errors",
        "@FlextErrorHandlingDecorators.handle_errors from flext_core"
    )

    # Import here to avoid circular imports
    from flext_core import FlextErrorHandlingDecorators

    return FlextErrorHandlingDecorators.handle_errors(func)


def legacy_performance_monitor(func: Any) -> Any:
    """Deprecated performance monitoring decorator.
    
    DEPRECATED: Use @FlextPerformanceDecorators.monitor from flext-core.
    """
    _issue_legacy_warning(
        "@legacy_performance_monitor",
        "@FlextPerformanceDecorators.monitor from flext_core"
    )

    # Import here to avoid circular imports
    from flext_core import FlextPerformanceDecorators

    return FlextPerformanceDecorators.monitor(func)


# Legacy mixin shims
class LegacyValidationMixin:
    """Deprecated validation mixin.
    
    DEPRECATED: Use FlextValidationMixin from flext-core instead.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Issue deprecation warning when subclassed."""
        super().__init_subclass__(**kwargs)
        _issue_legacy_warning(
            "LegacyValidationMixin",
            "FlextValidationMixin from flext_core"
        )


class LegacyInteractiveMixin:
    """Deprecated interactive mixin.
    
    DEPRECATED: Use FlextInteractiveMixin from flext-core instead.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Issue deprecation warning when subclassed."""
        super().__init_subclass__(**kwargs)
        _issue_legacy_warning(
            "LegacyInteractiveMixin",
            "FlextInteractiveMixin from flext_core"
        )


class LegacyServiceMixin:
    """Deprecated service mixin.
    
    DEPRECATED: Use FlextServiceMixin from flext-core instead.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Issue deprecation warning when subclassed."""
        super().__init_subclass__(**kwargs)
        _issue_legacy_warning(
            "LegacyServiceMixin",
            "FlextServiceMixin from flext_core"
        )


# Legacy configuration compatibility
def create_legacy_config(**kwargs: Any) -> Any:
    """Create legacy CLI configuration.
    
    DEPRECATED: Import CLIConfig directly and use standard instantiation.
    """
    _issue_legacy_warning(
        "create_legacy_config()",
        "CLIConfig(**kwargs) direct instantiation"
    )

    # Import here to avoid circular imports
    from flext_cli.config import CLIConfig

    return CLIConfig(**kwargs)


# Export legacy API for backward compatibility
__all__ = [
    # Legacy factories
    "LegacyFlextFactory",
    "CLIEntityFactory",
    # Legacy decorators
    "legacy_validate_result",
    "legacy_handle_errors",
    "legacy_performance_monitor",
    # Legacy mixins
    "LegacyValidationMixin",
    "LegacyInteractiveMixin",
    "LegacyServiceMixin",
    # Legacy configuration
    "create_legacy_config",
]

# Issue warning when module is imported
_issue_legacy_warning(
    "flext_cli.legacy module",
    "direct imports from flext_core and modern CLI patterns"
)
