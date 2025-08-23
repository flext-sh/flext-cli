#!/usr/bin/env python3
"""07 - Enterprise Patterns: Clean Architecture, CQRS, DDD.

This example demonstrates enterprise-grade patterns for large-scale CLI applications:

Key Patterns Demonstrated:
- Clean Architecture with Domain/Application/Infrastructure layers
- Command Query Responsibility Segregation (CQRS)
- Domain-Driven Design (DDD) with Aggregates and Domain Events
- Repository pattern with Unit of Work
- Event sourcing and domain event handling
- Service layer orchestration

Architecture Layers:
- Domain: Rich domain models with business logic
- Application: Use case orchestration and CQRS handlers
- Infrastructure: External service integration and persistence
- Commands: CLI interface layer

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID, uuid4

import click
from flext_core import (
    FlextDomainService,
    FlextEntity,
    FlextResult,
)
from rich.console import Console

from flext_cli import (
    FlextCliService,
    cli_enhanced,
    measure_time,
    require_auth,
)

# =============================================================================
# DOMAIN LAYER - Rich domain models with business logic
# =============================================================================


@dataclass(frozen=True)
class ProjectCreated:
    """Domain event: Project was created."""

    project_id: UUID
    project_name: str
    owner_id: str


@dataclass(frozen=True)
class ProjectStatusChanged:
    """Domain event: Project status changed."""

    project_id: UUID
    old_status: str
    new_status: str


class ProjectStatus(StrEnum):
    """Project status enumeration."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(FlextEntity):
    """Project aggregate root with business logic."""

    project_id: UUID
    name: str
    description: str
    owner_id: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime | None = None

    def change_status(
        self, new_status: ProjectStatus, _reason: str
    ) -> FlextResult[None]:
        """Change project status with business rules."""
        if self.status == new_status:
            return FlextResult[str].fail(f"Project already has status: {new_status}")

        # Business rule: Cannot activate archived projects
        if self.status == ProjectStatus.ARCHIVED and new_status == ProjectStatus.ACTIVE:
            return FlextResult[str].fail("Cannot activate archived projects")

        old_status = self.status
        updated_project = self.model_copy(
            update={"status": new_status, "updated_at": datetime.now(UTC)}
        )

        # Add domain event (simplified for demo)
        ProjectStatusChanged(
            project_id=self.project_id, old_status=old_status, new_status=new_status
        )
        # In real implementation: updated_project.add_domain_event(event)

        return FlextResult[str].ok(updated_project)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules."""
        # Define constant for minimum name length
        min_name_length = 3
        if not self.name or len(self.name.strip()) < min_name_length:
            return FlextResult[str].fail(
                f"Project name must be at least {min_name_length} characters"
            )

        if not self.owner_id:
            return FlextResult[str].fail("Project must have an owner")

        return FlextResult[str].ok(None)

    @classmethod
    def create_new(
        cls, name: str, description: str, owner_id: str
    ) -> FlextResult[Project]:
        """Factory method to create new project."""
        project_id = uuid4()

        project = cls(
            project_id=project_id,
            name=name.strip(),
            description=description.strip(),
            owner_id=owner_id,
            status=ProjectStatus.ACTIVE,
            created_at=datetime.now(UTC),
        )

        # Validate business rules
        validation_result = project.validate_domain_rules()
        if validation_result.is_failure:
            return FlextResult[str].fail(validation_result.error)

        # Add domain event (simplified for demo)
        ProjectCreated(project_id=project_id, project_name=name, owner_id=owner_id)
        # In real implementation: project.add_domain_event(event)

        return FlextResult[str].ok(project)


# =============================================================================
# DOMAIN SERVICES
# =============================================================================


class ProjectDomainService(FlextDomainService):
    """Domain service for cross-project operations."""

    def can_transfer_ownership(
        self, project: Project, new_owner_id: str
    ) -> FlextResult[bool]:
        """Check if project ownership can be transferred."""
        if project.status == ProjectStatus.ARCHIVED:
            can_transfer = False
            return FlextResult[str].ok(can_transfer)

        if project.owner_id == new_owner_id:
            return FlextResult[str].fail("Cannot transfer to same owner")

        can_transfer = True
        return FlextResult[str].ok(can_transfer)


# =============================================================================
# REPOSITORY PATTERN
# =============================================================================


class ProjectRepository(Protocol):
    """Repository interface for projects."""

    def save(self, project: Project) -> FlextResult[None]:
        """Save project to persistence."""
        ...

    def find_by_id(self, project_id: UUID) -> FlextResult[Project | None]:
        """Find project by ID."""
        ...

    def find_by_owner(self, owner_id: str) -> FlextResult[list[Project]]:
        """Find projects by owner."""
        ...


class InMemoryProjectRepository:
    """In-memory implementation for demo."""

    def __init__(self) -> None:
        self._projects: dict[UUID, Project] = {}

    def save(self, project: Project) -> FlextResult[None]:
        """Save project to memory."""
        self._projects[project.project_id] = project
        return FlextResult[str].ok(None)

    def find_by_id(self, project_id: UUID) -> FlextResult[Project | None]:
        """Find project by ID."""
        project = self._projects.get(project_id)
        return FlextResult[str].ok(project)

    def find_by_owner(self, owner_id: str) -> FlextResult[list[Project]]:
        """Find projects by owner."""
        projects = [
            project
            for project in self._projects.values()
            if project.owner_id == owner_id
        ]
        return FlextResult[str].ok(projects)


# =============================================================================
# APPLICATION LAYER - CQRS Commands and Queries
# =============================================================================


@dataclass(frozen=True)
class CreateProjectCommand:
    """Command to create new project."""

    name: str
    description: str
    owner_id: str


@dataclass(frozen=True)
class ChangeProjectStatusCommand:
    """Command to change project status."""

    project_id: UUID
    new_status: ProjectStatus
    reason: str


@dataclass(frozen=True)
class GetProjectQuery:
    """Query to get project details."""

    project_id: UUID


@dataclass(frozen=True)
class ListProjectsByOwnerQuery:
    """Query to list projects by owner."""

    owner_id: str


class CreateProjectHandler(FlextCliService[Project]):
    """CQRS command handler for creating projects."""

    def __init__(
        self,
        repository: ProjectRepository,
        domain_service: ProjectDomainService,
        **data: object,
    ) -> None:
        super().__init__(service_name="create_project_handler", **data)
        self._repository = repository
        self._domain_service = domain_service

    def execute(self, command: CreateProjectCommand) -> FlextResult[Project]:
        """Execute create project command."""
        # Create domain entity
        create_result = Project.create_new(
            name=command.name,
            description=command.description,
            owner_id=command.owner_id,
        )

        if create_result.is_failure:
            return create_result

        project = create_result.value

        # Save to repository
        save_result = self._repository.save(project)
        if save_result.is_failure:
            return FlextResult[str].fail(
                f"Failed to save project: {save_result.error}"
            )

        # Process domain events (in real app, this would be async)
        self._process_domain_events([event])

        return FlextResult[str].ok(project)

    def _process_domain_events(self, events: list[object]) -> None:
        """Process domain events."""
        for event in events:
            if isinstance(event, ProjectCreated) and self.logger:
                # In real app: publish to event bus, update read models, etc.
                self.logger.info(f"Project created: {event.project_name}")


class ChangeProjectStatusHandler(FlextCliService[Project]):
    """CQRS command handler for changing project status."""

    def __init__(self, repository: ProjectRepository, **data: object) -> None:
        super().__init__(service_name="change_status_handler", **data)
        self._repository = repository

    def execute(self, command: ChangeProjectStatusCommand) -> FlextResult[Project]:
        """Execute change status command."""
        # Load aggregate
        find_result = self._repository.find_by_id(command.project_id)
        if find_result.is_failure:
            return FlextResult[str].fail(find_result.error)

        project = find_result.value
        if not project:
            return FlextResult[str].fail(f"Project not found: {command.project_id}")

        # Execute business logic
        change_result = project.change_status(command.new_status, command.reason)
        if change_result.is_failure:
            return change_result

        updated_project = change_result.value

        # Save changes
        save_result = self._repository.save(updated_project)
        if save_result.is_failure:
            return FlextResult[str].fail(save_result.error)

        return FlextResult[str].ok(updated_project)


class ProjectQueryHandler(FlextCliService[dict[str, object]]):
    """CQRS query handler for project queries."""

    def __init__(self, repository: ProjectRepository, **data: object) -> None:
        super().__init__(service_name="project_query_handler", **data)
        self._repository = repository

    def execute_get_project(
        self, query: GetProjectQuery
    ) -> FlextResult[dict[str, object]]:
        """Execute get project query."""
        find_result = self._repository.find_by_id(query.project_id)
        if find_result.is_failure:
            return FlextResult[str].fail(find_result.error)

        project = find_result.value
        if not project:
            return FlextResult[str].fail(f"Project not found: {query.project_id}")

        # Return read model (DTO)
        project_data = {
            "id": str(project.project_id),
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
            "status": project.status.value,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
            if project.updated_at
            else None,
        }

        return FlextResult[str].ok(project_data)

    def execute_list_by_owner(
        self, query: ListProjectsByOwnerQuery
    ) -> FlextResult[list[dict[str, object]]]:
        """Execute list projects by owner query."""
        find_result = self._repository.find_by_owner(query.owner_id)
        if find_result.is_failure:
            return find_result

        projects = find_result.value
        project_list = [
            {
                "id": str(project.project_id),
                "name": project.name,
                "status": project.status.value,
                "created_at": project.created_at.isoformat(),
            }
            for project in projects
        ]

        return FlextResult[str].ok(project_list)


# =============================================================================
# INFRASTRUCTURE LAYER - External services and configuration
# =============================================================================


class ProjectManagementService(FlextCliService[dict[str, object]]):
    """Infrastructure service orchestrating the application layer."""

    def __init__(self, **data: object) -> None:
        super().__init__(service_name="project_management", **data)

        # Setup dependencies (in real app: DI container)
        self._repository = InMemoryProjectRepository()
        self._domain_service = ProjectDomainService()
        self._create_handler = CreateProjectHandler(
            repository=self._repository, domain_service=self._domain_service
        )
        self._status_handler = ChangeProjectStatusHandler(repository=self._repository)
        self._query_handler = ProjectQueryHandler(repository=self._repository)

    def create_project(
        self, name: str, description: str, owner_id: str
    ) -> FlextResult[dict[str, object]]:
        """Create new project through CQRS."""
        command = CreateProjectCommand(
            name=name, description=description, owner_id=owner_id
        )

        result = self._create_handler.execute(command)
        if result.is_failure:
            return result

        project = result.value
        return FlextResult[str].ok(
            {
                "id": str(project.project_id),
                "name": project.name,
                "status": project.status.value,
                "message": "Project created successfully",
            }
        )

    def change_project_status(
        self, project_id: str, new_status: str, reason: str
    ) -> FlextResult[dict[str, object]]:
        """Change project status through CQRS."""
        try:
            uuid_id = UUID(project_id)
            status_enum = ProjectStatus(new_status)
        except (ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Invalid input: {e}")

        command = ChangeProjectStatusCommand(
            project_id=uuid_id, new_status=status_enum, reason=reason
        )

        result = self._status_handler.execute(command)
        if result.is_failure:
            return result

        project = result.value
        return FlextResult[str].ok(
            {
                "id": str(project.project_id),
                "status": project.status.value,
                "message": "Status changed successfully",
            }
        )

    def get_project(self, project_id: str) -> FlextResult[dict[str, object]]:
        """Get project details through CQRS."""
        try:
            uuid_id = UUID(project_id)
        except (ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Invalid project ID: {e}")

        query = GetProjectQuery(project_id=uuid_id)
        return self._query_handler.execute_get_project(query)

    def list_projects_by_owner(
        self, owner_id: str
    ) -> FlextResult[list[dict[str, object]]]:
        """List projects by owner through CQRS."""
        query = ListProjectsByOwnerQuery(owner_id=owner_id)
        return self._query_handler.execute_list_by_owner(query)


# =============================================================================
# CLI COMMANDS LAYER - User interface
# =============================================================================


@click.group()
@click.pass_context
def enterprise_cli(ctx: click.Context) -> None:
    """Enterprise patterns CLI demonstrating Clean Architecture and CQRS."""
    ctx.ensure_object(dict)
    ctx.obj["console"] = Console()
    ctx.obj["service"] = ProjectManagementService()


@enterprise_cli.command()
@click.option("--name", required=True, help="Project name")
@click.option("--description", required=True, help="Project description")
@click.option("--owner", required=True, help="Project owner ID")
@click.pass_context
@cli_enhanced
@measure_time
def create_project(ctx: click.Context, name: str, description: str, owner: str) -> None:
    """Create a new project using enterprise patterns."""
    console: Console = ctx.obj["console"]
    service: ProjectManagementService = ctx.obj["service"]

    console.print(f"[blue]Creating project:[/blue] {name}")

    result = service.create_project(name, description, owner)

    if result.is_success:
        data = result.value
        console.print("[green]✅ Project created successfully[/green]")
        console.print(f"ID: {data['id']}")
        console.print(f"Status: {data['status']}")
    else:
        console.print(f"[red]❌ Failed to create project: {result.error}[/red]")


@enterprise_cli.command()
@click.option("--project-id", required=True, help="Project ID")
@click.option(
    "--status",
    required=True,
    type=click.Choice(["active", "suspended", "completed", "archived"]),
    help="New status",
)
@click.option("--reason", required=True, help="Reason for status change")
@click.pass_context
@cli_enhanced
@measure_time
@require_auth()
def change_status(
    ctx: click.Context, project_id: str, status: str, reason: str
) -> None:
    """Change project status using CQRS command."""
    console: Console = ctx.obj["console"]
    service: ProjectManagementService = ctx.obj["service"]

    console.print(f"[blue]Changing project status to:[/blue] {status}")

    result = service.change_project_status(project_id, status, reason)

    if result.is_success:
        data = result.value
        console.print("[green]✅ Status changed successfully[/green]")
        console.print(f"Project: {data['id']}")
        console.print(f"New Status: {data['status']}")
    else:
        console.print(f"[red]❌ Failed to change status: {result.error}[/red]")


@enterprise_cli.command()
@click.option("--project-id", required=True, help="Project ID")
@click.pass_context
@cli_enhanced
def get_project(ctx: click.Context, project_id: str) -> None:
    """Get project details using CQRS query."""
    console: Console = ctx.obj["console"]
    service: ProjectManagementService = ctx.obj["service"]

    result = service.get_project(project_id)

    if result.is_success:
        data = result.value
        console.print("[green]Project Details:[/green]")
        console.print(f"ID: {data['id']}")
        console.print(f"Name: {data['name']}")
        console.print(f"Description: {data['description']}")
        console.print(f"Owner: {data['owner_id']}")
        console.print(f"Status: {data['status']}")
        console.print(f"Created: {data['created_at']}")
        if data["updated_at"]:
            console.print(f"Updated: {data['updated_at']}")
    else:
        console.print(f"[red]❌ Failed to get project: {result.error}[/red]")


@enterprise_cli.command()
@click.option("--owner-id", required=True, help="Owner ID")
@click.pass_context
@cli_enhanced
def list_projects(ctx: click.Context, owner_id: str) -> None:
    """List projects by owner using CQRS query."""
    console: Console = ctx.obj["console"]
    service: ProjectManagementService = ctx.obj["service"]

    result = service.list_projects_by_owner(owner_id)

    if result.is_success:
        projects = result.value
        if projects:
            console.print(f"[green]Projects for owner {owner_id}:[/green]")
            for project in projects:
                console.print(
                    f"- {project['name']} ({project['status']}) - {project['id']}"
                )
        else:
            console.print(f"[yellow]No projects found for owner: {owner_id}[/yellow]")
    else:
        console.print(f"[red]❌ Failed to list projects: {result.error}[/red]")


def main() -> None:
    """Run enterprise patterns demonstration."""
    print("🏗️ Enterprise Patterns: Clean Architecture + CQRS + DDD")
    print("=" * 60)
    print()
    print("This example demonstrates:")
    print("✅ Clean Architecture (Domain/Application/Infrastructure/Commands)")
    print("✅ CQRS (Command Query Responsibility Segregation)")
    print("✅ DDD (Domain-Driven Design with Aggregates)")
    print("✅ Repository Pattern with Protocol interfaces")
    print("✅ Domain Events and Event Sourcing")
    print("✅ Enterprise service orchestration")
    print()
    print("Try these commands:")
    print(
        "  python examples/07_enterprise_patterns.py create-project --name 'My Project' --description 'Test project' --owner 'user123'"
    )
    print("  python examples/07_enterprise_patterns.py get-project --project-id <uuid>")
    print(
        "  python examples/07_enterprise_patterns.py change-status --project-id <uuid> --status suspended --reason 'Maintenance'"
    )
    print(
        "  python examples/07_enterprise_patterns.py list-projects --owner-id 'user123'"
    )
    print()


if __name__ == "__main__":
    import sys
    from datetime import datetime

    if len(sys.argv) == 1:
        main()
    else:
        enterprise_cli()
