"""FLEXT CLI Domain Package - Domain Entities, Value Objects, and Services.

This package implements the domain layer of FLEXT CLI following Domain-Driven
Design (DDD) principles with flext-core integration. Contains domain entities,
value objects, domain services, and business logic for CLI operations.

Domain Components:
    - Entities: CLICommand, CLIPlugin, CLISession with business logic
    - Value Objects: CLIContext, CLIExecutionContext for immutable state
    - Domain Services: CLICommandService, CLISessionService for business operations
    - Enums: CommandStatus, CommandType for type-safe domain modeling

Architecture:
    - Domain-Driven Design (DDD) with rich domain entities
    - flext-core integration (FlextEntity, FlextValueObject, FlextResult)
    - Clean Architecture domain layer isolation
    - Type-safe domain modeling with comprehensive validation
    - Business rule enforcement through domain entities

Current Implementation Status:
    ✅ Core domain entities with business logic
    ✅ Domain services for command and session management
    ✅ Value objects for context and execution tracking
    ✅ flext-core integration for patterns and validation
    ✅ Type-safe enums for domain modeling
    ✅ FlextResult-based error handling
    ⚠️ Basic implementation (TODO: Sprint 2 - enhance domain features)

Domain Entities:
    - CLICommand: Command execution with lifecycle management
    - CLIPlugin: Plugin management with dependencies and validation
    - CLISession: User session tracking with command history

Value Objects:
    - CLIContext: Immutable CLI context with configuration
    - CLIExecutionContext: Command execution metadata tracking

Domain Services:
    - CLICommandService: Command creation and validation
    - CLISessionService: Session management and validation
    - CLIServiceContainer: Service registration and dependency injection

Enums and Types:
    - CommandStatus: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    - CommandType: CLI, SYSTEM for command classification

Usage Examples:
    Creating commands:
    >>> command = CLICommand(
    ...     name="test", command_line="echo hello", command_type=CommandType.SYSTEM
    ... )
    >>> command.start_execution()

    Domain services:
    >>> service = CLICommandService()
    >>> result = service.create_command("test", "echo hello", "system")

Integration:
    - Used by application layer for business logic
    - Integrates with infrastructure for persistence
    - Provides domain model for CLI operations
    - Supports Clean Architecture and DDD patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_cli.domain.cli_services import CLIServiceContainer
from flext_cli.domain.entities import (
    CLICommand,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)

__all__: list[str] = [
    "CLICommand",
    "CLIPlugin",
    "CLIServiceContainer",
    "CLISession",
    "CommandStatus",
    "CommandType",
]
