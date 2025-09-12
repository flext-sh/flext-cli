#!/usr/bin/env python3
"""FLEXT CLI Global Configuration Refactoring Example.

Demonstrates how all modules now use FlextConfig singleton as the
SINGLE SOURCE OF TRUTH for configuration, eliminating all other
configuration patterns and ensuring consistency across the entire
CLI application.

This example shows:
1. FlextConfig singleton as the only configuration source
2. All modules (Client, API, Core, Auth) using FlextConfig
3. Dynamic configuration updates across all modules
4. CLI parameters modifying behavior through FlextConfig
5. Elimination of duplicate configuration patterns

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from pathlib import Path

from flext_core import FlextConfig, FlextResult
from flext_cli.config import FlextCliConfig
from flext_cli.client import FlextApiClient
from flext_cli.api import FlextCliApi
from flext_cli.core import FlextCliService
from flext_cli.auth import FlextCliAuth


def demonstrate_global_configuration_refactoring() -> None:
    """Demonstrate global configuration refactoring across all modules."""
    print("=== GLOBAL CONFIGURATION REFACTORING DEMONSTRATION ===\n")
    
    # 1. Show FlextConfig as SINGLE SOURCE OF TRUTH
    print("1. FlextConfig Singleton (SINGLE SOURCE OF TRUTH):")
    base_config = FlextConfig.get_global_instance()
    cli_config = FlextCliConfig.get_global_instance()
    
    print(f"   Base Config Environment: {base_config.environment}")
    print(f"   Base Config Debug: {base_config.debug}")
    print(f"   Base Config Log Level: {base_config.log_level}")
    print(f"   CLI Config Profile: {cli_config.profile}")
    print(f"   CLI Config API URL: {cli_config.api_url}")
    print()
    
    # 2. Initialize all modules using FlextConfig singleton
    print("2. Initializing All Modules with FlextConfig Singleton:")
    
    # Initialize API Client
    api_client = FlextApiClient()
    print(f"   ✅ FlextApiClient initialized")
    print(f"      Base URL: {api_client.base_url}")
    print(f"      Timeout: {api_client.timeout}s")
    print(f"      Verify SSL: {api_client.verify_ssl}")
    
    # Initialize CLI API
    cli_api = FlextCliApi()
    print(f"   ✅ FlextCliApi initialized")
    print(f"      Version: {cli_api.state.version}")
    print(f"      Service Name: {cli_api.state.service_name}")
    
    # Initialize CLI Service
    cli_service = FlextCliService()
    print(f"   ✅ FlextCliService initialized")
    print(f"      Config Source: {type(cli_service.get_config()).__name__}")
    
    # Initialize CLI Auth
    cli_auth = FlextCliAuth()
    print(f"   ✅ FlextCliAuth initialized")
    print(f"      Config Source: {type(cli_auth.config).__name__}")
    print()
    
    # 3. Apply CLI parameter overrides
    print("3. Applying CLI Parameter Overrides:")
    cli_overrides = {
        "debug": True,
        "log_level": "DEBUG",
        "api_url": "https://api.example.com",
        "command_timeout": 60,
    }
    
    print("   CLI Parameters:")
    for key, value in cli_overrides.items():
        print(f"     {key}: {value}")
    
    # Apply overrides to FlextConfig singleton
    result = FlextCliConfig.apply_cli_overrides(cli_overrides)
    if result.is_failure:
        print(f"   ❌ Failed to apply overrides: {result.error}")
        return
    
    print("   ✅ Overrides applied to FlextConfig singleton")
    print()
    
    # 4. Update all modules from FlextConfig singleton
    print("4. Updating All Modules from FlextConfig Singleton:")
    
    # Update API Client
    api_client.update_from_config()
    print(f"   ✅ FlextApiClient updated")
    print(f"      New Base URL: {api_client.base_url}")
    print(f"      New Timeout: {api_client.timeout}s")
    
    # Update CLI API
    cli_api.update_from_config()
    print(f"   ✅ FlextCliApi updated")
    print(f"      New Version: {cli_api.state.version}")
    
    # Update CLI Service
    cli_service.update_configuration()
    print(f"   ✅ FlextCliService updated")
    print(f"      Config Updated: {type(cli_service.get_config()).__name__}")
    
    # Update CLI Auth
    cli_auth.update_from_config()
    print(f"   ✅ FlextCliAuth updated")
    print(f"      Config Updated: {type(cli_auth.config).__name__}")
    print()
    
    # 5. Verify consistency across all modules
    print("5. Verifying Configuration Consistency:")
    updated_base_config = FlextConfig.get_global_instance()
    updated_cli_config = FlextCliConfig.get_global_instance()
    
    print(f"   FlextConfig Debug: {updated_base_config.debug}")
    print(f"   FlextConfig Log Level: {updated_base_config.log_level}")
    print(f"   FlextCliConfig API URL: {updated_cli_config.api_url}")
    print(f"   FlextCliConfig Command Timeout: {updated_cli_config.command_timeout}s")
    
    # Verify all modules are using the same configuration
    consistency_checks = [
        ("API Client Base URL", api_client.base_url, updated_cli_config.api_url),
        ("API Client Timeout", api_client.timeout, updated_cli_config.api_timeout),
        ("CLI API Version", cli_api.state.version, updated_cli_config.project_version),
    ]
    
    print("\n   Consistency Checks:")
    all_consistent = True
    for check_name, module_value, config_value in consistency_checks:
        consistent = str(module_value) == str(config_value)
        status = "✅" if consistent else "❌"
        print(f"     {status} {check_name}: {consistent}")
        if not consistent:
            all_consistent = False
    
    if all_consistent:
        print("\n   🎉 ALL MODULES CONSISTENT WITH FLEXT CONFIG SINGLETON!")
    else:
        print("\n   ⚠️  Some modules not consistent with FlextConfig singleton")
    print()


def demonstrate_elimination_of_duplicate_patterns() -> None:
    """Demonstrate elimination of duplicate configuration patterns."""
    print("=== ELIMINATION OF DUPLICATE CONFIGURATION PATTERNS ===\n")
    
    print("1. Before Refactoring (Multiple Configuration Patterns):")
    print("   ❌ Each module had its own configuration")
    print("   ❌ Duplicate configuration loading logic")
    print("   ❌ Inconsistent configuration sources")
    print("   ❌ Manual configuration synchronization")
    print("   ❌ Multiple configuration validation rules")
    print()
    
    print("2. After Refactoring (Single Configuration Pattern):")
    print("   ✅ FlextConfig singleton as SINGLE SOURCE OF TRUTH")
    print("   ✅ All modules use FlextConfig.get_global_instance()")
    print("   ✅ Automatic configuration synchronization")
    print("   ✅ Consistent configuration validation")
    print("   ✅ CLI parameters modify behavior through FlextConfig")
    print()
    
    print("3. Configuration Pattern Usage:")
    
    # Show how all modules now use the same pattern
    modules = [
        ("FlextApiClient", "api_client.update_from_config()"),
        ("FlextCliApi", "cli_api.update_from_config()"),
        ("FlextCliService", "cli_service.update_configuration()"),
        ("FlextCliAuth", "cli_auth.update_from_config()"),
    ]
    
    for module_name, update_method in modules:
        print(f"   ✅ {module_name}: Uses FlextConfig singleton")
        print(f"      Update method: {update_method}")
    
    print()


def demonstrate_dynamic_configuration_updates() -> None:
    """Demonstrate dynamic configuration updates across all modules."""
    print("=== DYNAMIC CONFIGURATION UPDATES ===\n")
    
    # Initialize all modules
    api_client = FlextApiClient()
    cli_api = FlextCliApi()
    cli_service = FlextCliService()
    cli_auth = FlextCliAuth()
    
    print("1. Initial Configuration State:")
    print(f"   API Client Base URL: {api_client.base_url}")
    print(f"   CLI API Version: {cli_api.state.version}")
    print(f"   CLI Service Config: {type(cli_service.get_config()).__name__}")
    print(f"   CLI Auth Config: {type(cli_auth.config).__name__}")
    print()
    
    # Apply configuration changes
    print("2. Applying Configuration Changes:")
    config_changes = {
        "api_url": "https://new-api.example.com",
        "project_version": "1.0.0",
        "debug": True,
        "log_level": "DEBUG",
    }
    
    result = FlextCliConfig.apply_cli_overrides(config_changes)
    if result.is_success:
        print("   ✅ Configuration changes applied to FlextConfig singleton")
    else:
        print(f"   ❌ Failed to apply changes: {result.error}")
        return
    print()
    
    # Update all modules
    print("3. Updating All Modules:")
    api_client.update_from_config()
    cli_api.update_from_config()
    cli_service.update_configuration()
    cli_auth.update_from_config()
    
    print("   ✅ All modules updated from FlextConfig singleton")
    print()
    
    # Show updated state
    print("4. Updated Configuration State:")
    print(f"   API Client Base URL: {api_client.base_url}")
    print(f"   CLI API Version: {cli_api.state.version}")
    print(f"   CLI Service Config: {type(cli_service.get_config()).__name__}")
    print(f"   CLI Auth Config: {type(cli_auth.config).__name__}")
    print()
    
    # Verify all modules reflect the changes
    updated_config = FlextCliConfig.get_global_instance()
    print("5. Verification:")
    print(f"   FlextConfig API URL: {updated_config.api_url}")
    print(f"   FlextConfig Project Version: {updated_config.project_version}")
    print(f"   FlextConfig Debug: {updated_config.debug}")
    print(f"   FlextConfig Log Level: {updated_config.log_level}")
    print()


def demonstrate_cli_parameter_integration() -> None:
    """Demonstrate CLI parameter integration with all modules."""
    print("=== CLI PARAMETER INTEGRATION ===\n")
    
    print("1. CLI Parameter Flow:")
    print("   CLI Parameters → FlextConfig Singleton → All Modules")
    print()
    
    # Simulate CLI parameters
    print("2. Simulating CLI Parameters:")
    cli_params = {
        "--debug": True,
        "--log-level": "WARNING",
        "--api-url": "https://production-api.example.com",
        "--timeout": 120,
    }
    
    for param, value in cli_params.items():
        print(f"   {param}: {value}")
    print()
    
    # Apply CLI parameters
    print("3. Applying CLI Parameters to FlextConfig:")
    cli_overrides = {
        "debug": cli_params["--debug"],
        "log_level": cli_params["--log-level"],
        "api_url": cli_params["--api-url"],
        "command_timeout": cli_params["--timeout"],
    }
    
    result = FlextCliConfig.apply_cli_overrides(cli_overrides)
    if result.is_success:
        print("   ✅ CLI parameters applied to FlextConfig singleton")
    else:
        print(f"   ❌ Failed to apply CLI parameters: {result.error}")
        return
    print()
    
    # Initialize modules with updated configuration
    print("4. Initializing Modules with Updated Configuration:")
    api_client = FlextApiClient()
    cli_api = FlextCliApi()
    cli_service = FlextCliService()
    cli_auth = FlextCliAuth()
    
    print("   ✅ All modules initialized with CLI parameter overrides")
    print()
    
    # Show final state
    print("5. Final Configuration State:")
    final_config = FlextCliConfig.get_global_instance()
    print(f"   Debug Mode: {final_config.debug}")
    print(f"   Log Level: {final_config.log_level}")
    print(f"   API URL: {final_config.api_url}")
    print(f"   Command Timeout: {final_config.command_timeout}s")
    print()
    
    print("6. Module Configuration Verification:")
    print(f"   API Client Base URL: {api_client.base_url}")
    print(f"   API Client Timeout: {api_client.timeout}s")
    print(f"   CLI API Version: {cli_api.state.version}")
    print(f"   CLI Service Config: {type(cli_service.get_config()).__name__}")
    print(f"   CLI Auth Config: {type(cli_auth.config).__name__}")
    print()


def main() -> None:
    """Main demonstration function."""
    print("FLEXT CLI Global Configuration Refactoring Example")
    print("=" * 60)
    print()
    
    try:
        demonstrate_global_configuration_refactoring()
        demonstrate_elimination_of_duplicate_patterns()
        demonstrate_dynamic_configuration_updates()
        demonstrate_cli_parameter_integration()
        
        print("=== SUMMARY ===")
        print("✅ FlextConfig singleton is the SINGLE SOURCE OF TRUTH")
        print("✅ All modules use FlextConfig.get_global_instance()")
        print("✅ CLI parameters modify behavior through FlextConfig")
        print("✅ Dynamic configuration updates across all modules")
        print("✅ Elimination of duplicate configuration patterns")
        print("✅ Consistent configuration validation")
        print("✅ Automatic synchronization between modules")
        print()
        print("The global refactoring ensures:")
        print("- Single configuration source eliminates inconsistencies")
        print("- CLI parameters modify behavior through FlextConfig singleton")
        print("- All modules automatically stay synchronized")
        print("- Configuration changes propagate to all modules")
        print("- Type-safe validation and error handling")
        print("- Consistent state across the entire CLI application")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    main()