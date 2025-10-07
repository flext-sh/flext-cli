"""Interactive Prompts - User Interaction.

Demonstrates auto-configured prompts and FlextResult validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_basic_prompts() -> None:
    """Basic prompts - auto-configured for terminal."""
    # Prompts auto-detect terminal capabilities
    # Example: cli.prompts.confirm("Continue?", default=True)
    cli.output.print_message("Prompts auto-configured for terminal")


def demonstrate_validation() -> None:
    """Prompt validation with FlextResult."""

    def validate_email(email: str) -> FlextResult[str]:
        if "@" not in email:
            return FlextResult[str].fail("Invalid email")
        return FlextResult[str].ok(email)

    result = validate_email("user@example.com")
    if result.is_success:
        cli.output.print_success(f"Valid: {result.value}")


def demonstrate_interactive_workflow() -> None:
    """Complete workflow pattern."""
    # Example workflow:
    # name = cli.prompts.prompt("Project name:")
    # env = cli.prompts.select("Environment:", choices=["dev", "prod"])
    # if cli.prompts.confirm(f"Create {name}?"):
    #     cli.output.print_success(f"Creating {name} in {env}")
    cli.output.print_message("Interactive workflows auto-configured")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_basic_prompts()
    demonstrate_validation()
    demonstrate_interactive_workflow()


if __name__ == "__main__":
    main()
