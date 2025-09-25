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
- FLEXT-CLI foundation patterns (NO Click imports)

Architecture Layers:
- Domain: Rich domain models with business logic
- Application: Use case orchestration and CQRS handlers
- Infrastructure: External service integration and persistence
- Commands: CLI interface layer using FlextCliCommands and FlextCliApi

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol, cast, override
from uuid import UUID, uuid4

from pydantic import Field

from flext_cli import (
    FlextCliApi,
    FlextCliCommands,
    FlextCliService,
)
from flext_core import (
    FlextModels,
    FlextResult,
    FlextService,
    FlextTypes,
)


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


class Project(FlextModels.AggregateRoot):  # type: ignore[misc]
    """Project aggregate root with business logic."""

    project_id: UUID
    name: str
    description: str
    owner_id: str
    status: ProjectStatus
    # Timestamp fields inherited from Entity base class
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def change_status(
        self, new_status: ProjectStatus, _reason: str
    ) -> FlextResult[None]:
        """Change project status with business rules."""
        if self.status == new_status:
            return FlextResult[None].fail(f"Project already has status: {new_status}")

        # Business rule: Cannot activate archived projects
        if self.status == ProjectStatus.ARCHIVED and new_status == ProjectStatus.ACTIVE:
            return FlextResult[None].fail("Cannot activate archived projects")

        old_status = self.status
        self.model_copy(update={"status": new_status, "updated_at": datetime.now(UTC)})

        # Add domain event (simplified for demo)
        ProjectStatusChanged(
            project_id=self.project_id, old_status=old_status, new_status=new_status
        )
        # In real implementation: updated_project.add_domain_event(event)

        return FlextResult[None].ok(None)

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain business rules."""
        # Define constant for minimum name length
        min_name_length = 3
        if not self.name or len(self.name.strip()) < min_name_length:
            return FlextResult[None].fail(
                f"Project name must be at least {min_name_length} characters"
            )

        if not self.owner_id:
            return FlextResult[None].fail("Project must have an owner")

        return FlextResult[None].ok(None)

    @classmethod
    def create_new(
        cls, name: str, description: str, owner_id: str
    ) -> FlextResult[Project]:
        """Factory method to create new project."""
        project_id = uuid4()

        project = cls(
            id=str(project_id),  # FlextModels requires 'id' as string
            project_id=project_id,
            name=name.strip(),
            description=description.strip(),
            owner_id=owner_id,
            status=ProjectStatus.ACTIVE,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            domain_events=[],
        )

        # Validate business rules
        validation_result = project.validate_domain_rules()
        if validation_result.is_failure:
            return FlextResult[Project].fail(
                str(validation_result.error)
                if validation_result.error
                else "Validation failed"
            )

        # Add domain event (simplified for demo)
        ProjectCreated(project_id=project_id, project_name=name, owner_id=owner_id)
        # In real implementation: project.add_domain_event(event)

        return FlextResult[Project].ok(project)


class ProjectDomainService(FlextService[dict[str, object]]):  # type: ignore[misc]
    """Domain service for cross-project operations."""

    @override
    def execute(self) -> FlextResult[dict[str, object]]:
        """Execute method required by FlextService base class."""
        return FlextResult[dict[str, object]].ok({"service": "project_domain"})

    def can_transfer_ownership(
        self, project: Project, new_owner_id: str
    ) -> FlextResult[bool]:
        """Check if project ownership can be transferred."""
        if project.status == ProjectStatus.ARCHIVED:
            can_transfer = False
            return FlextResult[bool].ok(can_transfer)

        if project.owner_id == new_owner_id:
            return FlextResult[bool].fail("Cannot transfer to same owner")

        can_transfer = True
        return FlextResult[bool].ok(can_transfer)


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
        """Initialize in-memory project repository."""
        self._projects: dict[UUID, Project] = {}

    def save(self, project: Project) -> FlextResult[None]:
        """Save project to memory."""
        self._projects[project.project_id] = project
        return FlextResult[None].ok(None)

    def find_by_id(self, project_id: UUID) -> FlextResult[Project | None]:
        """Find project by ID."""
        project = self._projects.get(project_id)
        return FlextResult[Project | None].ok(project)

    def find_by_owner(self, owner_id: str) -> FlextResult[list[Project]]:
        """Find projects by owner."""
        projects = [
            project
            for project in self._projects.values()
            if project.owner_id == owner_id
        ]
        return FlextResult[list[Project]].ok(projects)


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


class CreateProjectHandler:
    """CQRS command handler for creating projects."""

    def __init__(
        self,
        repository: ProjectRepository,
        service: ProjectDomainService,
    ) -> None:
        """Initialize create project handler with dependencies."""
        self._repository = repository
        self._domain_service = service

    def handle(self, command: CreateProjectCommand) -> FlextResult[Project]:
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
            return FlextResult[Project].fail(
                f"Failed to save project: {save_result.error}"
            )

        # Process domain events (in real app, this would be async)
        project_created_event = {
            "type": "ProjectCreated",
            "project_id": str(project.project_id),
            "timestamp": "2025-01-27",
        }
        self._process_domain_events([project_created_event])

        return FlextResult[Project].ok(project)

    def _process_domain_events(self, events: FlextTypes.Core.List) -> None:
        """Process domain events."""
        for event in events:
            if (
                isinstance(event, dict)
                and cast("dict[str, object]", event).get("type") == "ProjectCreated"
            ):
                event_dict: dict[str, object] = cast("dict[str, object]", event)
                # In real app: publish to event bus, update read models, etc.
                event_type: str = str(event_dict.get("type", "unknown"))
                project_id: str = str(event_dict.get("project_id", "unknown"))
                print(f"Processing domain event: {event_type} for project {project_id}")


class ChangeProjectStatusHandler:
    """CQRS command handler for changing project status."""

    def __init__(self, repository: ProjectRepository) -> None:
        """Initialize change status handler with repository."""
        self._repository = repository

    def handle(self, command: ChangeProjectStatusCommand) -> FlextResult[Project]:
        """Execute change status command."""
        # Load aggregate
        find_result = self._repository.find_by_id(command.project_id)
        if find_result.is_failure:
            return FlextResult[Project].fail(
                str(find_result.error) if find_result.error else "Find failed"
            )

        project = find_result.value
        if not project:
            return FlextResult[Project].fail(f"Project not found: {command.project_id}")

        # Execute business logic
        change_result = project.change_status(command.new_status, command.reason)
        if change_result.is_failure:
            return FlextResult[Project].fail(
                str(change_result.error)
                if change_result.error
                else "Status change failed"
            )

        # Save changes
        save_result = self._repository.save(
            project
        )  # Use original project, not updated_project
        if save_result.is_failure:
            return FlextResult[Project].fail(
                str(save_result.error) if save_result.error else "Save failed"
            )

        return FlextResult[Project].ok(
            project
        )  # Return the project, not updated_project


class ProjectQueryHandler:
    """CQRS query handler for project queries."""

    def __init__(self, repository: ProjectRepository) -> None:
        """Initialize query handler with repository."""
        self._repository = repository

    def execute_get_project(
        self, query: GetProjectQuery
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute get project query."""
        find_result = self._repository.find_by_id(query.project_id)
        if find_result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(
                str(find_result.error) if find_result.error else "Find failed"
            )

        project = find_result.value
        if not project:
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Project not found: {query.project_id}"
            )

        # Return read model (DTO)
        project_data = {
            "id": str(project.project_id),
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
            "status": project.status.value,
            "created_at": str(project.created_at),
            "updated_at": str(project.updated_at) if project.updated_at else None,
        }

        return FlextResult[FlextTypes.Core.Dict].ok(dict(project_data))

    def execute_list_by_owner(
        self, query: ListProjectsByOwnerQuery
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """Execute list projects by owner query."""
        find_result = self._repository.find_by_owner(query.owner_id)
        if find_result.is_failure:
            return FlextResult[list[FlextTypes.Core.Dict]].fail(
                str(find_result.error) if find_result.error else "Find by owner failed"
            )

        projects = find_result.value
        project_list = [
            {
                "id": str(project.project_id),
                "name": project.name,
                "status": project.status.value,
                "created_at": str(project.created_at),
            }
            for project in projects
        ]

        # Cast to fix variance issue
        project_list_obj: list[FlextTypes.Core.Dict] = [{**p} for p in project_list]
        return FlextResult[list[FlextTypes.Core.Dict]].ok(project_list_obj)


class ProjectManagementService(FlextCliService):
    """Infrastructure service orchestrating the application layer."""

    _repository: InMemoryProjectRepository
    _create_handler: CreateProjectHandler
    _status_handler: ChangeProjectStatusHandler
    _query_handler: ProjectQueryHandler

    def __init__(self, **data: object) -> None:
        """Initialize CQRS service with dependencies."""
        super().__init__(**data)

        # Setup dependencies (in real app: DI container)
        self._repository = InMemoryProjectRepository()
        service = ProjectDomainService()
        self._create_handler = CreateProjectHandler(
            repository=self._repository, service=service
        )
        self._status_handler = ChangeProjectStatusHandler(repository=self._repository)
        self._query_handler = ProjectQueryHandler(repository=self._repository)

    def execute(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute method required by FlextService base class."""
        return FlextResult[FlextTypes.Core.Dict].ok({
            "status": "project_management service active"
        })

    def create_project(
        self, name: str, description: str, owner_id: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Create new project through CQRS."""
        command = CreateProjectCommand(
            name=name, description=description, owner_id=owner_id
        )

        result = self._create_handler.handle(command)
        if result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(
                str(result.error) if result.error else "Create failed"
            )

        project = result.value
        return FlextResult[FlextTypes.Core.Dict].ok({
            "id": str(project.project_id),
            "name": project.name,
            "status": project.status.value,
            "message": "Project created successfully",
        })

    def change_project_status(
        self, project_id: str, new_status: str, reason: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Change project status through CQRS."""
        try:
            uuid_id = UUID(project_id)
            status_enum = ProjectStatus(new_status)
        except (ValueError, TypeError) as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Invalid input: {e}")

        command = ChangeProjectStatusCommand(
            project_id=uuid_id, new_status=status_enum, reason=reason
        )

        result = self._status_handler.handle(command)
        if result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(
                str(result.error) if result.error else "Status change failed"
            )

        project = result.value
        return FlextResult[FlextTypes.Core.Dict].ok({
            "id": str(project.project_id),
            "status": project.status.value,
            "message": "Status changed successfully",
        })

    def get_project(self, project_id: str) -> FlextResult[FlextTypes.Core.Dict]:
        """Get project details through CQRS."""
        try:
            uuid_id = UUID(project_id)
        except (ValueError, TypeError) as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Invalid project ID: {e}")

        query = GetProjectQuery(project_id=uuid_id)
        return self._query_handler.execute_get_project(query)

    def list_projects_by_owner(
        self, owner_id: str
    ) -> FlextResult[list[FlextTypes.Core.Dict]]:
        """List projects by owner through CQRS."""
        query = ListProjectsByOwnerQuery(owner_id=owner_id)
        return self._query_handler.execute_list_by_owner(query)


class EnterpriseCliApplication:
    """Enterprise CLI application using flext-cli patterns exclusively."""

    def __init__(self) -> None:
        """Initialize enterprise CLI application."""
        self.cli_api = FlextCliApi()
        self.api_client = FlextCliService()
        self.service = ProjectManagementService()

    def create_cli_interface(self) -> FlextResult[FlextCliCommands]:
        """Create enterprise CLI interface using flext-cli patterns."""
        try:
            # Initialize CLI main instance
            cli_main = FlextCliCommands(
                name="enterprise-cli",
                description="Enterprise patterns CLI demonstrating Clean Architecture and CQRS",
            )

            # Register command groups
            self._register_project_commands(cli_main)

            return FlextResult[FlextCliCommands].ok(cli_main)

        except Exception as e:
            return FlextResult[FlextCliCommands].fail(
                f"CLI interface creation failed: {e}"
            )

    def _register_project_commands(self, cli_main: FlextCliCommands) -> None:
        """Register project management commands."""
        # Create commands and unwrap FlextResult values
        create_cmd = self.cli_api.create_command(
            name="create",
            description="Create a new project using enterprise patterns",
            handler=self._handle_create_project,
            arguments=["--name", "--description", "--owner"],
        )
        change_status_cmd = self.cli_api.create_command(
            name="change-status",
            description="Change project status using CQRS command",
            handler=self._handle_change_status,
            arguments=["--project-id", "--status", "--reason"],
        )
        get_cmd = self.cli_api.create_command(
            name="get",
            description="Get project details using CQRS query",
            handler=self._handle_get_project,
            arguments=["--project-id"],
        )
        list_cmd = self.cli_api.create_command(
            name="list",
            description="List projects by owner using CQRS query",
            handler=self._handle_list_projects,
            arguments=["--owner-id"],
        )

        # Unwrap commands for registration - only include successful commands
        project_commands: dict[str, object] = {}
        if create_cmd.is_success:
            project_commands["create"] = create_cmd.unwrap()
        if change_status_cmd.is_success:
            project_commands["change-status"] = change_status_cmd.unwrap()
        if get_cmd.is_success:
            project_commands["get"] = get_cmd.unwrap()
        if list_cmd.is_success:
            project_commands["list"] = list_cmd.unwrap()

        cli_main.register_command_group(
            name="project",
            commands=project_commands,
            description="Project management commands using enterprise patterns",
        )

    def _handle_create_project(self, **kwargs: object) -> FlextResult[None]:
        """Handle create project command."""
        name = str(kwargs.get("name", ""))
        description = str(kwargs.get("description", ""))
        owner = str(kwargs.get("owner", ""))

        if not all([name, description, owner]):
            return FlextResult[None].fail("Name, description, and owner are required")

        self.cli_api.display_message(f"Creating project: {name}", message_type="info")
        result = self.service.create_project(name, description, owner)

        if result.is_success:
            data = result.unwrap()
            self.cli_api.display_data(data=data, format_type="table")
        else:
            self.cli_api.display_message(
                f"Failed to create project: {result.error}", message_type="error"
            )

        return FlextResult[None].ok(None)

    def _handle_change_status(self, **kwargs: object) -> FlextResult[None]:
        """Handle change project status command."""
        project_id = str(kwargs.get("project_id", ""))
        status = str(kwargs.get("status", ""))
        reason = str(kwargs.get("reason", ""))

        if not all([project_id, status, reason]):
            return FlextResult[None].fail("Project ID, status, and reason are required")

        valid_statuses = ["active", "suspended", "completed", "archived"]
        if status not in valid_statuses:
            return FlextResult[None].fail(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )

        self.cli_api.display_message(
            f"Changing project status to: {status}", message_type="info"
        )
        result = self.service.change_project_status(project_id, status, reason)

        if result.is_success:
            data = result.unwrap()
            self.cli_api.display_data(data=data, format_type="table")
        else:
            self.cli_api.display_message(
                f"Failed to change status: {result.error}", message_type="error"
            )

        return FlextResult[None].ok(None)

    def _handle_get_project(self, **kwargs: object) -> FlextResult[None]:
        """Handle get project command."""
        project_id = str(kwargs.get("project_id", ""))

        if not project_id:
            return FlextResult[None].fail("Project ID is required")

        result = self.service.get_project(project_id)

        if result.is_success:
            data = result.unwrap()
            self.cli_api.display_data(data=data, format_type="table")
        else:
            self.cli_api.display_message(
                f"Failed to get project: {result.error}", message_type="error"
            )

        return FlextResult[None].ok(None)

    def _handle_list_projects(self, **kwargs: object) -> FlextResult[None]:
        """Handle list projects command."""
        owner_id = str(kwargs.get("owner_id", ""))

        if not owner_id:
            return FlextResult[None].fail("Owner ID is required")

        result = self.service.list_projects_by_owner(owner_id)

        if result.is_success:
            projects = result.unwrap()
            if projects:
                self.cli_api.display_message(
                    f"Projects for owner {owner_id}:", message_type="info"
                )
                for project in projects:
                    project_info = (
                        f"- {project['name']} ({project['status']}) - {project['id']}"
                    )
                    self.cli_api.display_message(project_info, message_type="info")
            else:
                self.cli_api.display_message(
                    f"No projects found for owner: {owner_id}", message_type="warning"
                )
        else:
            self.cli_api.display_message(
                f"Failed to list projects: {result.error}", message_type="error"
            )

        return FlextResult[None].ok(None)


def main() -> None:
    """Run enterprise patterns demonstration using flext-cli patterns."""
    try:
        # Create application instance
        app = EnterpriseCliApplication()

        # Create CLI interface
        cli_result = app.create_cli_interface()
        if cli_result.is_failure:
            app.cli_api.display_message(
                f"CLI creation failed: {cli_result.error}", message_type="error"
            )
            return

        # Run CLI
        cli_main = cli_result.unwrap()
        execution_result = cli_main.execute()

        if execution_result.is_failure:
            app.cli_api.display_message(
                f"CLI execution failed: {execution_result.error}", message_type="error"
            )

    except Exception as e:
        cli_api = FlextCliApi()
        cli_api.display_message(f"Enterprise CLI error: {e}", message_type="error")


if __name__ == "__main__":
    main()
