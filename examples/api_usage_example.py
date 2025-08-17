#!/usr/bin/env python3
"""Example of FLEXT CLI API usage.

This example demonstrates the real functionality implemented in the FLEXT CLI API.
It shows how to use all the major features without placeholders or mockups.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import operator
import tempfile
from datetime import UTC, datetime
from typing import cast

from flext_cli import CLICommand, FlextCliApi

# Constants
PREVIEW_LENGTH_LIMIT = 200


class FlextCliDemoRunner:
    """Demo runner following SOLID principles for reduced complexity."""

    def __init__(self) -> None:
      """Initialize demo runner with API instance."""
      self.api = FlextCliApi()

    def configure_service(self) -> bool:
      """Configure the CLI service with demo settings."""
      config = {
          "project_name": "example-project",
          "project_version": "1.0.0",
          "project_description": "Example CLI usage",
          "debug": True,
          "log_level": "DEBUG",
      }

      return self.api.flext_cli_configure(config)

    def check_health_status(self) -> dict[str, object]:
      """Check and display health status."""
      health = self.api.flext_cli_health()
      python_version = health["python_version"]
      if isinstance(python_version, str):
          pass
      return health

    def create_demo_commands(self) -> tuple[bool, bool]:
      """Create demonstration CLI commands."""
      # Create system command
      result = self.api.flext_cli_create_command(
          "list-files",
          "ls -la",
          description="List files in directory",
          command_type="system",
          timeout_seconds=10,
      )

      system_success = False
      if result.success:
          cast("CLICommand", result.data)  # Cast to proper type
          system_success = True

      # Create script command using secure temporary directory

      secure_backup_dir = tempfile.mkdtemp(prefix="backup_")

      script_result = self.api.flext_cli_create_command(
          "backup-data",
          "python backup_script.py",
          description="Backup application data",
          command_type="script",
          environment_vars={"BACKUP_DIR": secure_backup_dir},
          timeout_seconds=300,
      )

      script_success = False
      if script_result.success:
          cast("CLICommand", script_result.data)  # Cast to proper type
          script_success = True

      return system_success, script_success

    def manage_sessions(self) -> str | None:
      """Create and manage demo sessions."""
      session_result = self.api.flext_cli_create_session("demo_user")
      if session_result.success:
          session_id = session_result.unwrap()

          # Get active sessions
          sessions = self.api.flext_cli_get_sessions()
          if session_id in sessions:
              sessions[session_id]

          return session_id
      return None

    def _create_calculator_handler(self) -> callable:
      """Create calculator handler function."""

      def calculator_handler(operation: str, a: float, b: float) -> dict[str, object]:
          """Simple calculator handler."""
          operations = {
              "add": operator.add,
              "subtract": operator.sub,
              "multiply": operator.mul,
              "divide": lambda x, y: x / y if y != 0 else None,
          }

          if operation not in operations:
              return {"error": f"Unknown operation: {operation}"}

          result = operations[operation](a, b)
          return {
              "operation": operation,
              "operands": [a, b],
              "result": result,
              "timestamp": datetime.now(UTC).isoformat(),
          }

      return calculator_handler

    def register_and_execute_handlers(self) -> bool:
      """Register and execute demonstration handlers."""
      calculator_handler = self._create_calculator_handler()

      # Register the handler
      register_result = self.api.flext_cli_register_handler(
          "calculator",
          calculator_handler,
      )
      if register_result.success:
          # Execute the handler
          exec_result = self.api.flext_cli_execute_handler(
              "calculator",
              "multiply",
              15.5,
              4.2,
          )

          if exec_result.success:
              exec_result.unwrap()
              return True

      return False

    def _get_sample_data(self) -> list[dict[str, object]]:
      """Get sample data for demonstrations."""
      return [
          {"name": "Alice", "age": 30, "city": "New York"},
          {"name": "Bob", "age": 25, "city": "San Francisco"},
          {"name": "Carol", "age": 35, "city": "Chicago"},
      ]

    def demonstrate_formatting(self) -> bool:
      """Demonstrate data formatting and rendering capabilities."""
      sample_data = self._get_sample_data()

      # Render as table (default)
      table_result = self.api.flext_cli_render_with_context(sample_data)
      if table_result.success:
          # Render with custom context
          context_result = self.api.flext_cli_render_with_context(
              sample_data,
              {"format": "json", "title": "User Data"},
          )
          if context_result.success:
              rendered = context_result.unwrap()
              (
                  rendered[:PREVIEW_LENGTH_LIMIT] + "..."
                  if len(rendered) > PREVIEW_LENGTH_LIMIT
                  else rendered
              )
              return True

      return False

    def demonstrate_export(self) -> bool:
      """Demonstrate data export functionality."""
      sample_data = self._get_sample_data()
      export_data = {
          "users": sample_data,
          "metadata": {
              "export_time": datetime.now(UTC).isoformat(),
              "total_records": len(sample_data),
              "format": "json",
          },
      }

      # Use the formatting functionality
      formatted_json = self.api.flext_cli_format(export_data, "json")
      if formatted_json:
          # Parse and pretty print
          try:
              json.loads(formatted_json)
              return True
          except json.JSONDecodeError:
              return True

      return False

    def show_registry_summary(self) -> None:
      """Show summary of all registries."""
      self.api.flext_cli_get_commands()
      self.api.flext_cli_get_sessions()
      self.api.flext_cli_get_plugins()
      handlers = self.api.flext_cli_get_handlers()

      if handlers:
          for _name, _info in handlers.items():
              pass

    def run_complete_demo(self) -> bool:
      """Run the complete demonstration workflow."""
      # Execute all demo steps
      success_flags = [
          self.configure_service(),
          bool(self.check_health_status()),
          any(self.create_demo_commands()),
          self.manage_sessions() is not None,
          self.register_and_execute_handlers(),
          self.demonstrate_formatting(),
          self.demonstrate_export(),
      ]

      self.show_registry_summary()

      success = all(success_flags)
      if success:
          pass

      return success


def main() -> None:
    """Run FLEXT CLI API demonstration using SOLID principles."""
    demo_runner = FlextCliDemoRunner()
    demo_runner.run_complete_demo()


if __name__ == "__main__":
    main()
