"""FLEXT CLI Commands Package - CLI Command Implementations and Management.

This package contains all CLI command implementations for FLEXT CLI, organized
into logical groups with consistent patterns and interfaces. Implements the
presentation layer of Clean Architecture with Click framework integration.

Current Command Groups:
    - auth: Authentication and authorization commands (login, logout, status)
    - config: Configuration management commands (get, set, list, reset)
    - debug: Debug and diagnostic commands (info, paths, validate, health)

Planned Command Groups (docs/TODO.md):
    - pipeline: Pipeline management (list, create, start, stop, status)
    - service: Service management (list, status, restart, logs)
    - data: Data operations (extract, transform, load, validate)
    - monitor: Monitoring and observability (metrics, logs, traces)

Architecture:
    - Click framework for command-line interface structure
    - Rich console integration for enhanced terminal UX
    - Clean Architecture presentation layer patterns
    - Consistent error handling and validation
    - Type-safe command implementations

Current Implementation Status:
    ✅ Authentication commands (auth group)
    ✅ Configuration commands (config group)
    ✅ Debug commands (debug group)
    ❌ Pipeline management not implemented (TODO: Sprint 1)
    ❌ Service management not implemented (TODO: Sprint 1)
    ❌ Data operations not implemented (TODO: Sprint 4)
    ❌ Monitoring commands not implemented (TODO: Sprint 7)

Command Patterns:
    - Click groups for logical command organization
    - Rich console for beautiful output and formatting
    - Context passing for configuration and state
    - Consistent error handling and user feedback
    - Type-safe parameter validation

TODO (docs/TODO.md):
    Sprint 1: Implement pipeline management commands
    Sprint 1: Implement service management commands
    Sprint 4: Implement data operation commands
    Sprint 7: Implement monitoring and observability commands
    Sprint 8: Implement interactive mode and wizards

Integration:
    - Registered with main CLI application in cli.py
    - Uses domain services for business logic
    - Integrates with configuration and authentication
    - Provides user interface for FLEXT ecosystem

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
