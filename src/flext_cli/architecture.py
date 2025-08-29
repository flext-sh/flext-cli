"""FLEXT CLI Clean Architecture - Base classes following FLEXT patterns.

Clean Architecture base classes implementing flext-core patterns.
Follows FLEXT_REFACTORING_PROMPT.md layered architecture.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar, object

from flext_cli.models_simple import FlextResult

T = TypeVar("T")
U = TypeVar("U")


# =============================================================================
# DOMAIN LAYER - Business Logic Core
# =============================================================================


class FlextDomainService(ABC):
    """Base class for domain services - FLEXT pattern."""

    def __init__(self) -> None:
        self._name = self.__class__.__name__

    @abstractmethod
    def execute(self, *args, **kwargs) -> FlextResult[object]:
        """Execute domain service operation."""


class FlextModels.Entity(ABC):
    """Base entity class following FLEXT patterns."""

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def validate_business_rules(self) -> FlextResult[None]:
        """Validate entity business rules."""


# =============================================================================
# APPLICATION LAYER - Use Cases and Handlers
# =============================================================================


class FlextUseCase[T, U](ABC):
    """Base use case following Clean Architecture - FLEXT pattern."""

    @abstractmethod
    def execute(self, request: T) -> FlextResult[U]:
        """Execute use case with request/response pattern."""


class FlextCommandHandler[T](ABC):
    """Command handler following CQRS - FLEXT pattern."""

    @abstractmethod
    def handle(self, command: T) -> FlextResult[None]:
        """Handle command operation."""


class FlextQueryHandler[T, U](ABC):
    """Query handler following CQRS - FLEXT pattern."""

    @abstractmethod
    def handle(self, query: T) -> FlextResult[U]:
        """Handle query operation."""


# =============================================================================
# INFRASTRUCTURE LAYER - External Concerns
# =============================================================================


class FlextRepository[T](ABC):
    """Repository pattern base - FLEXT pattern."""

    @abstractmethod
    def save(self, entity: T) -> FlextResult[T]:
        """Save entity to storage."""

    @abstractmethod
    def find_by_id(self, entity_id: str) -> FlextResult[T]:
        """Find entity by ID."""

    @abstractmethod
    def find_all(self) -> FlextResult[list[T]]:
        """Find all entities."""


class FlextExternalService(ABC):
    """External service integration base - FLEXT pattern."""

    @abstractmethod
    def is_available(self) -> FlextResult[bool]:
        """Check if external service is available."""


# =============================================================================
# PRESENTATION LAYER - CLI Interface
# =============================================================================


class FlextCliController(ABC):
    """CLI controller base following MVC - FLEXT pattern."""

    def __init__(self) -> None:
        self._name = self.__class__.__name__

    @abstractmethod
    def handle_command(self, args: dict[str, object]) -> FlextResult[None]:
        """Handle CLI command with arguments."""


# =============================================================================
# FACTORY PATTERNS - Object Creation
# =============================================================================


class FlextFactory[T](ABC):
    """Factory pattern base - FLEXT pattern."""

    @abstractmethod
    def create(self, **kwargs) -> FlextResult[T]:
        """Create instance with validation."""


# =============================================================================
# DECORATOR PATTERNS - Cross-cutting Concerns
# =============================================================================


def flext_use_case(use_case_name: str):
    """Decorator for use cases - FLEXT pattern."""

    def decorator(cls):
        cls._use_case_name = use_case_name
        return cls

    return decorator


def flext_command_handler(command_name: str):
    """Decorator for command handlers - FLEXT pattern."""

    def decorator(cls):
        cls._command_name = command_name
        return cls

    return decorator


def flext_query_handler(query_name: str):
    """Decorator for query handlers - FLEXT pattern."""

    def decorator(cls):
        cls._query_name = query_name
        return cls

    return decorator


__all__ = [
    # Presentation Layer
    "FlextCliController",
    "FlextCommandHandler",
    # Domain Layer
    "FlextDomainService",
    "FlextModels.Entity",
    "FlextExternalService",
    # Factory Pattern
    "FlextFactory",
    "FlextQueryHandler",
    # Infrastructure Layer
    "FlextRepository",
    # Application Layer
    "FlextUseCase",
    "flext_command_handler",
    "flext_query_handler",
    # Decorators
    "flext_use_case",
]
