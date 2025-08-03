"""FLEXT CLI Infrastructure Package - Infrastructure Layer Implementation.

This package implements the infrastructure layer of Clean Architecture for
FLEXT CLI, providing external concerns like dependency injection, configuration
management, and external service integrations.

Infrastructure Components:
    - Container: Dependency injection container (SimpleDIContainer + CLIContainer)
    - Config: Infrastructure-level configuration management
    - Repository implementations: Data persistence abstractions
    - External service integrations: FlexCore, FLEXT services

Architecture:
    - Clean Architecture infrastructure layer patterns
    - Dependency injection with service registration
    - Configuration management with environment variable support
    - Mock repository implementations for development
    - Integration points for external systems

Current Implementation Status:
    ✅ SimpleDIContainer with basic dependency management
    ✅ CLIContainer with service registration
    ✅ Infrastructure configuration with path expansion
    ✅ Mock repository implementations
    ⚠️ Basic implementation (TODO: Sprint 1 - FlextContainer migration)
    ❌ Real repository implementations not implemented (TODO: Sprint 2)

TODO (docs/TODO.md):
    Sprint 1: Migrate from SimpleDIContainer to FlextContainer
    Sprint 1: Add FlexCore and FLEXT service client integrations
    Sprint 2: Implement real repository patterns with persistence
    Sprint 3: Add external API client implementations
    Sprint 7: Add monitoring and observability infrastructure

Components:
    container.py:
        - SimpleDIContainer: Basic dependency injection (temporary)
        - CLIContainer: CLI-specific service container
        - Mock repositories for development and testing

    config.py:
        - CLIConfig: Infrastructure configuration class
        - Path expansion utilities and directory management
        - Environment variable integration

Integration:
    - Used by application layer for external concerns
    - Provides Clean Architecture infrastructure boundary
    - Integrates with flext-core container patterns
    - Supports testing with mock implementations

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
