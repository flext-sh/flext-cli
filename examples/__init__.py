# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import examples.constants as _examples_constants

    constants = _examples_constants
    import examples.ex_01_getting_started as _examples_ex_01_getting_started
    from examples.constants import (
        FlextCliExamplesConstants,
        FlextCliExamplesConstants as c,
    )

    ex_01_getting_started = _examples_ex_01_getting_started
    import examples.ex_02_output_formatting as _examples_ex_02_output_formatting
    from examples.ex_01_getting_started import FlextCliGettingStarted

    ex_02_output_formatting = _examples_ex_02_output_formatting
    import examples.ex_03_interactive_prompts as _examples_ex_03_interactive_prompts
    from examples.ex_02_output_formatting import (
        advanced_output_example,
        display_database_results,
        display_project_structure,
        display_with_panels,
        export_report,
        monitor_live_metrics,
        process_with_status,
        your_cli_function,
    )

    ex_03_interactive_prompts = _examples_ex_03_interactive_prompts
    import examples.ex_04_file_operations as _examples_ex_04_file_operations
    from examples.ex_03_interactive_prompts import (
        authenticate_user,
        database_setup_wizard,
        delete_database,
        flext_configuration_wizard,
        flext_confirm_prompts,
        flext_numeric_prompts,
        flext_prompt_with_validation,
        get_user_configuration,
        prompts,
        select_environment,
        validate_email_input,
    )

    ex_04_file_operations = _examples_ex_04_file_operations
    import examples.ex_05_authentication as _examples_ex_05_authentication
    from examples.ex_04_file_operations import (
        backup_config_files,
        create_processing_summary,
        export_database_report,
        export_multi_format,
        generate_output_files,
        list_project_files,
        load_config_auto_detect,
        load_deployment_config,
        load_user_preferences,
        process_file_pipeline,
        save_deployment_config,
        save_user_preferences,
        show_directory_tree,
        validate_and_import_data,
        validate_and_transform_data,
    )

    ex_05_authentication = _examples_ex_05_authentication
    import examples.ex_06_configuration as _examples_ex_06_configuration
    from examples.ex_05_authentication import (
        call_authenticated_api,
        complete_auth_workflow,
        get_saved_token,
        login_to_service,
        logout,
        refresh_token_if_needed,
        show_session_info,
        validate_current_token,
        validate_user_credentials,
    )

    ex_06_configuration = _examples_ex_06_configuration
    import examples.ex_07_plugin_system as _examples_ex_07_plugin_system
    from examples.ex_06_configuration import (
        apply_environment_overrides,
        get_cli_settings,
        initialize_services,
        load_application_config,
        load_environment_config,
        load_profile_config,
        show_config_locations,
        show_environment_variables,
        validate_app_config,
    )

    ex_07_plugin_system = _examples_ex_07_plugin_system
    import examples.ex_08_shell_interaction as _examples_ex_08_shell_interaction
    from examples.ex_07_plugin_system import (
        ConfigurablePlugin,
        DataExportPlugin,
        LifecyclePlugin,
        MyAppPluginManager,
        ReportGeneratorPlugin,
        load_plugins_from_directory,
    )

    ex_08_shell_interaction = _examples_ex_08_shell_interaction
    import examples.ex_09_performance_optimization as _examples_ex_09_performance_optimization
    from examples.ex_08_shell_interaction import (
        CommandHistory,
        InteractiveShell,
        handle_config_command,
        handle_list_command,
        handle_multiline_input,
        handle_status_command,
    )

    ex_09_performance_optimization = _examples_ex_09_performance_optimization
    import examples.ex_10_testing_utilities as _examples_ex_10_testing_utilities
    from examples.ex_09_performance_optimization import (
        LazyDataLoader,
        demonstrate_caching,
        demonstrate_lazy_loading,
        efficient_cli_usage,
        efficient_table_display,
        expensive_calculation,
        process_large_dataset,
        stream_large_file,
    )

    ex_10_testing_utilities = _examples_ex_10_testing_utilities
    import examples.ex_11_complete_integration as _examples_ex_11_complete_integration
    from examples.ex_10_testing_utilities import (
        full_workflow_command,
        interactive_command,
        my_cli_command,
        risky_operation,
        save_config_command,
        test_cli_command,
        test_error_scenarios,
        test_file_operations,
        test_integration,
        test_interactive_command,
    )

    ex_11_complete_integration = _examples_ex_11_complete_integration
    import examples.ex_12_pydantic_driven_cli as _examples_ex_12_pydantic_driven_cli
    from examples.ex_11_complete_integration import (
        DataManagerCLI,
        process_with_railway_pattern,
    )

    ex_12_pydantic_driven_cli = _examples_ex_12_pydantic_driven_cli
    import examples.ex_14_advanced_file_formats as _examples_ex_14_advanced_file_formats
    from examples.ex_12_pydantic_driven_cli import (
        convert_and_validate_with_pydantic,
        create_database_config_from_cli,
        demonstrate_auto_cli_generation,
        demonstrate_nested_models,
        deploy_application,
        execute_deploy_from_cli,
        perform_connection_test,
        show_common_cli_params,
        validate_business_rules,
        validate_required_fields,
    )

    ex_14_advanced_file_formats = _examples_ex_14_advanced_file_formats
    import examples.ex_15_plugin as _examples_ex_15_plugin
    from examples.ex_14_advanced_file_formats import (
        copy_file_with_verification,
        export_data_multi_format,
        export_to_csv,
        import_from_csv,
        load_any_format_file,
        main,
        process_binary_file,
        process_text_file,
    )

    ex_15_plugin = _examples_ex_15_plugin
    import examples.models as _examples_models
    from examples.ex_15_plugin import (
        DataProcessorPlugin,
        ExamplePlugin,
        demonstrate_plugin_commands,
    )

    models = _examples_models
    import examples.protocols as _examples_protocols
    from examples.models import FlextCliExamplesModels, FlextCliExamplesModels as m

    protocols = _examples_protocols
    import examples.typings as _examples_typings
    from examples.protocols import (
        FlextCliExamplesProtocols,
        FlextCliExamplesProtocols as p,
    )

    typings = _examples_typings
    import examples.utilities as _examples_utilities
    from examples.typings import FlextCliExamplesTypes, FlextCliExamplesTypes as t

    utilities = _examples_utilities
    from examples.utilities import (
        FlextCliExamplesUtilities,
        FlextCliExamplesUtilities as u,
    )
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
_LAZY_IMPORTS = {
    "CommandHistory": ("examples.ex_08_shell_interaction", "CommandHistory"),
    "ConfigurablePlugin": ("examples.ex_07_plugin_system", "ConfigurablePlugin"),
    "DataExportPlugin": ("examples.ex_07_plugin_system", "DataExportPlugin"),
    "DataManagerCLI": ("examples.ex_11_complete_integration", "DataManagerCLI"),
    "DataProcessorPlugin": ("examples.ex_15_plugin", "DataProcessorPlugin"),
    "ExamplePlugin": ("examples.ex_15_plugin", "ExamplePlugin"),
    "FlextCliExamplesConstants": ("examples.constants", "FlextCliExamplesConstants"),
    "FlextCliExamplesModels": ("examples.models", "FlextCliExamplesModels"),
    "FlextCliExamplesProtocols": ("examples.protocols", "FlextCliExamplesProtocols"),
    "FlextCliExamplesTypes": ("examples.typings", "FlextCliExamplesTypes"),
    "FlextCliExamplesUtilities": ("examples.utilities", "FlextCliExamplesUtilities"),
    "FlextCliGettingStarted": (
        "examples.ex_01_getting_started",
        "FlextCliGettingStarted",
    ),
    "InteractiveShell": ("examples.ex_08_shell_interaction", "InteractiveShell"),
    "LazyDataLoader": ("examples.ex_09_performance_optimization", "LazyDataLoader"),
    "LifecyclePlugin": ("examples.ex_07_plugin_system", "LifecyclePlugin"),
    "MyAppPluginManager": ("examples.ex_07_plugin_system", "MyAppPluginManager"),
    "ReportGeneratorPlugin": ("examples.ex_07_plugin_system", "ReportGeneratorPlugin"),
    "advanced_output_example": (
        "examples.ex_02_output_formatting",
        "advanced_output_example",
    ),
    "apply_environment_overrides": (
        "examples.ex_06_configuration",
        "apply_environment_overrides",
    ),
    "authenticate_user": ("examples.ex_03_interactive_prompts", "authenticate_user"),
    "backup_config_files": ("examples.ex_04_file_operations", "backup_config_files"),
    "c": ("examples.constants", "FlextCliExamplesConstants"),
    "call_authenticated_api": (
        "examples.ex_05_authentication",
        "call_authenticated_api",
    ),
    "complete_auth_workflow": (
        "examples.ex_05_authentication",
        "complete_auth_workflow",
    ),
    "constants": "examples.constants",
    "convert_and_validate_with_pydantic": (
        "examples.ex_12_pydantic_driven_cli",
        "convert_and_validate_with_pydantic",
    ),
    "copy_file_with_verification": (
        "examples.ex_14_advanced_file_formats",
        "copy_file_with_verification",
    ),
    "create_database_config_from_cli": (
        "examples.ex_12_pydantic_driven_cli",
        "create_database_config_from_cli",
    ),
    "create_processing_summary": (
        "examples.ex_04_file_operations",
        "create_processing_summary",
    ),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "database_setup_wizard": (
        "examples.ex_03_interactive_prompts",
        "database_setup_wizard",
    ),
    "delete_database": ("examples.ex_03_interactive_prompts", "delete_database"),
    "demonstrate_auto_cli_generation": (
        "examples.ex_12_pydantic_driven_cli",
        "demonstrate_auto_cli_generation",
    ),
    "demonstrate_caching": (
        "examples.ex_09_performance_optimization",
        "demonstrate_caching",
    ),
    "demonstrate_lazy_loading": (
        "examples.ex_09_performance_optimization",
        "demonstrate_lazy_loading",
    ),
    "demonstrate_nested_models": (
        "examples.ex_12_pydantic_driven_cli",
        "demonstrate_nested_models",
    ),
    "demonstrate_plugin_commands": (
        "examples.ex_15_plugin",
        "demonstrate_plugin_commands",
    ),
    "deploy_application": ("examples.ex_12_pydantic_driven_cli", "deploy_application"),
    "display_database_results": (
        "examples.ex_02_output_formatting",
        "display_database_results",
    ),
    "display_project_structure": (
        "examples.ex_02_output_formatting",
        "display_project_structure",
    ),
    "display_with_panels": ("examples.ex_02_output_formatting", "display_with_panels"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "efficient_cli_usage": (
        "examples.ex_09_performance_optimization",
        "efficient_cli_usage",
    ),
    "efficient_table_display": (
        "examples.ex_09_performance_optimization",
        "efficient_table_display",
    ),
    "ex_01_getting_started": "examples.ex_01_getting_started",
    "ex_02_output_formatting": "examples.ex_02_output_formatting",
    "ex_03_interactive_prompts": "examples.ex_03_interactive_prompts",
    "ex_04_file_operations": "examples.ex_04_file_operations",
    "ex_05_authentication": "examples.ex_05_authentication",
    "ex_06_configuration": "examples.ex_06_configuration",
    "ex_07_plugin_system": "examples.ex_07_plugin_system",
    "ex_08_shell_interaction": "examples.ex_08_shell_interaction",
    "ex_09_performance_optimization": "examples.ex_09_performance_optimization",
    "ex_10_testing_utilities": "examples.ex_10_testing_utilities",
    "ex_11_complete_integration": "examples.ex_11_complete_integration",
    "ex_12_pydantic_driven_cli": "examples.ex_12_pydantic_driven_cli",
    "ex_14_advanced_file_formats": "examples.ex_14_advanced_file_formats",
    "ex_15_plugin": "examples.ex_15_plugin",
    "execute_deploy_from_cli": (
        "examples.ex_12_pydantic_driven_cli",
        "execute_deploy_from_cli",
    ),
    "expensive_calculation": (
        "examples.ex_09_performance_optimization",
        "expensive_calculation",
    ),
    "export_data_multi_format": (
        "examples.ex_14_advanced_file_formats",
        "export_data_multi_format",
    ),
    "export_database_report": (
        "examples.ex_04_file_operations",
        "export_database_report",
    ),
    "export_multi_format": ("examples.ex_04_file_operations", "export_multi_format"),
    "export_report": ("examples.ex_02_output_formatting", "export_report"),
    "export_to_csv": ("examples.ex_14_advanced_file_formats", "export_to_csv"),
    "flext_configuration_wizard": (
        "examples.ex_03_interactive_prompts",
        "flext_configuration_wizard",
    ),
    "flext_confirm_prompts": (
        "examples.ex_03_interactive_prompts",
        "flext_confirm_prompts",
    ),
    "flext_numeric_prompts": (
        "examples.ex_03_interactive_prompts",
        "flext_numeric_prompts",
    ),
    "flext_prompt_with_validation": (
        "examples.ex_03_interactive_prompts",
        "flext_prompt_with_validation",
    ),
    "full_workflow_command": (
        "examples.ex_10_testing_utilities",
        "full_workflow_command",
    ),
    "generate_output_files": (
        "examples.ex_04_file_operations",
        "generate_output_files",
    ),
    "get_cli_settings": ("examples.ex_06_configuration", "get_cli_settings"),
    "get_saved_token": ("examples.ex_05_authentication", "get_saved_token"),
    "get_user_configuration": (
        "examples.ex_03_interactive_prompts",
        "get_user_configuration",
    ),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "handle_config_command": (
        "examples.ex_08_shell_interaction",
        "handle_config_command",
    ),
    "handle_list_command": ("examples.ex_08_shell_interaction", "handle_list_command"),
    "handle_multiline_input": (
        "examples.ex_08_shell_interaction",
        "handle_multiline_input",
    ),
    "handle_status_command": (
        "examples.ex_08_shell_interaction",
        "handle_status_command",
    ),
    "import_from_csv": ("examples.ex_14_advanced_file_formats", "import_from_csv"),
    "initialize_services": ("examples.ex_06_configuration", "initialize_services"),
    "interactive_command": ("examples.ex_10_testing_utilities", "interactive_command"),
    "list_project_files": ("examples.ex_04_file_operations", "list_project_files"),
    "load_any_format_file": (
        "examples.ex_14_advanced_file_formats",
        "load_any_format_file",
    ),
    "load_application_config": (
        "examples.ex_06_configuration",
        "load_application_config",
    ),
    "load_config_auto_detect": (
        "examples.ex_04_file_operations",
        "load_config_auto_detect",
    ),
    "load_deployment_config": (
        "examples.ex_04_file_operations",
        "load_deployment_config",
    ),
    "load_environment_config": (
        "examples.ex_06_configuration",
        "load_environment_config",
    ),
    "load_plugins_from_directory": (
        "examples.ex_07_plugin_system",
        "load_plugins_from_directory",
    ),
    "load_profile_config": ("examples.ex_06_configuration", "load_profile_config"),
    "load_user_preferences": (
        "examples.ex_04_file_operations",
        "load_user_preferences",
    ),
    "login_to_service": ("examples.ex_05_authentication", "login_to_service"),
    "logout": ("examples.ex_05_authentication", "logout"),
    "m": ("examples.models", "FlextCliExamplesModels"),
    "main": ("examples.ex_14_advanced_file_formats", "main"),
    "models": "examples.models",
    "monitor_live_metrics": (
        "examples.ex_02_output_formatting",
        "monitor_live_metrics",
    ),
    "my_cli_command": ("examples.ex_10_testing_utilities", "my_cli_command"),
    "p": ("examples.protocols", "FlextCliExamplesProtocols"),
    "perform_connection_test": (
        "examples.ex_12_pydantic_driven_cli",
        "perform_connection_test",
    ),
    "process_binary_file": (
        "examples.ex_14_advanced_file_formats",
        "process_binary_file",
    ),
    "process_file_pipeline": (
        "examples.ex_04_file_operations",
        "process_file_pipeline",
    ),
    "process_large_dataset": (
        "examples.ex_09_performance_optimization",
        "process_large_dataset",
    ),
    "process_text_file": ("examples.ex_14_advanced_file_formats", "process_text_file"),
    "process_with_railway_pattern": (
        "examples.ex_11_complete_integration",
        "process_with_railway_pattern",
    ),
    "process_with_status": ("examples.ex_02_output_formatting", "process_with_status"),
    "prompts": ("examples.ex_03_interactive_prompts", "prompts"),
    "protocols": "examples.protocols",
    "r": ("flext_core.result", "FlextResult"),
    "refresh_token_if_needed": (
        "examples.ex_05_authentication",
        "refresh_token_if_needed",
    ),
    "risky_operation": ("examples.ex_10_testing_utilities", "risky_operation"),
    "s": ("flext_core.service", "FlextService"),
    "save_config_command": ("examples.ex_10_testing_utilities", "save_config_command"),
    "save_deployment_config": (
        "examples.ex_04_file_operations",
        "save_deployment_config",
    ),
    "save_user_preferences": (
        "examples.ex_04_file_operations",
        "save_user_preferences",
    ),
    "select_environment": ("examples.ex_03_interactive_prompts", "select_environment"),
    "show_common_cli_params": (
        "examples.ex_12_pydantic_driven_cli",
        "show_common_cli_params",
    ),
    "show_config_locations": ("examples.ex_06_configuration", "show_config_locations"),
    "show_directory_tree": ("examples.ex_04_file_operations", "show_directory_tree"),
    "show_environment_variables": (
        "examples.ex_06_configuration",
        "show_environment_variables",
    ),
    "show_session_info": ("examples.ex_05_authentication", "show_session_info"),
    "stream_large_file": (
        "examples.ex_09_performance_optimization",
        "stream_large_file",
    ),
    "t": ("examples.typings", "FlextCliExamplesTypes"),
    "test_cli_command": ("examples.ex_10_testing_utilities", "test_cli_command"),
    "test_error_scenarios": (
        "examples.ex_10_testing_utilities",
        "test_error_scenarios",
    ),
    "test_file_operations": (
        "examples.ex_10_testing_utilities",
        "test_file_operations",
    ),
    "test_integration": ("examples.ex_10_testing_utilities", "test_integration"),
    "test_interactive_command": (
        "examples.ex_10_testing_utilities",
        "test_interactive_command",
    ),
    "typings": "examples.typings",
    "u": ("examples.utilities", "FlextCliExamplesUtilities"),
    "utilities": "examples.utilities",
    "validate_and_import_data": (
        "examples.ex_04_file_operations",
        "validate_and_import_data",
    ),
    "validate_and_transform_data": (
        "examples.ex_04_file_operations",
        "validate_and_transform_data",
    ),
    "validate_app_config": ("examples.ex_06_configuration", "validate_app_config"),
    "validate_business_rules": (
        "examples.ex_12_pydantic_driven_cli",
        "validate_business_rules",
    ),
    "validate_current_token": (
        "examples.ex_05_authentication",
        "validate_current_token",
    ),
    "validate_email_input": (
        "examples.ex_03_interactive_prompts",
        "validate_email_input",
    ),
    "validate_required_fields": (
        "examples.ex_12_pydantic_driven_cli",
        "validate_required_fields",
    ),
    "validate_user_credentials": (
        "examples.ex_05_authentication",
        "validate_user_credentials",
    ),
    "x": ("flext_core.mixins", "FlextMixins"),
    "your_cli_function": ("examples.ex_02_output_formatting", "your_cli_function"),
}

__all__ = [
    "CommandHistory",
    "ConfigurablePlugin",
    "DataExportPlugin",
    "DataManagerCLI",
    "DataProcessorPlugin",
    "ExamplePlugin",
    "FlextCliExamplesConstants",
    "FlextCliExamplesModels",
    "FlextCliExamplesProtocols",
    "FlextCliExamplesTypes",
    "FlextCliExamplesUtilities",
    "FlextCliGettingStarted",
    "InteractiveShell",
    "LazyDataLoader",
    "LifecyclePlugin",
    "MyAppPluginManager",
    "ReportGeneratorPlugin",
    "advanced_output_example",
    "apply_environment_overrides",
    "authenticate_user",
    "backup_config_files",
    "c",
    "call_authenticated_api",
    "complete_auth_workflow",
    "constants",
    "convert_and_validate_with_pydantic",
    "copy_file_with_verification",
    "create_database_config_from_cli",
    "create_processing_summary",
    "d",
    "database_setup_wizard",
    "delete_database",
    "demonstrate_auto_cli_generation",
    "demonstrate_caching",
    "demonstrate_lazy_loading",
    "demonstrate_nested_models",
    "demonstrate_plugin_commands",
    "deploy_application",
    "display_database_results",
    "display_project_structure",
    "display_with_panels",
    "e",
    "efficient_cli_usage",
    "efficient_table_display",
    "ex_01_getting_started",
    "ex_02_output_formatting",
    "ex_03_interactive_prompts",
    "ex_04_file_operations",
    "ex_05_authentication",
    "ex_06_configuration",
    "ex_07_plugin_system",
    "ex_08_shell_interaction",
    "ex_09_performance_optimization",
    "ex_10_testing_utilities",
    "ex_11_complete_integration",
    "ex_12_pydantic_driven_cli",
    "ex_14_advanced_file_formats",
    "ex_15_plugin",
    "execute_deploy_from_cli",
    "expensive_calculation",
    "export_data_multi_format",
    "export_database_report",
    "export_multi_format",
    "export_report",
    "export_to_csv",
    "flext_configuration_wizard",
    "flext_confirm_prompts",
    "flext_numeric_prompts",
    "flext_prompt_with_validation",
    "full_workflow_command",
    "generate_output_files",
    "get_cli_settings",
    "get_saved_token",
    "get_user_configuration",
    "h",
    "handle_config_command",
    "handle_list_command",
    "handle_multiline_input",
    "handle_status_command",
    "import_from_csv",
    "initialize_services",
    "interactive_command",
    "list_project_files",
    "load_any_format_file",
    "load_application_config",
    "load_config_auto_detect",
    "load_deployment_config",
    "load_environment_config",
    "load_plugins_from_directory",
    "load_profile_config",
    "load_user_preferences",
    "login_to_service",
    "logout",
    "m",
    "main",
    "models",
    "monitor_live_metrics",
    "my_cli_command",
    "p",
    "perform_connection_test",
    "process_binary_file",
    "process_file_pipeline",
    "process_large_dataset",
    "process_text_file",
    "process_with_railway_pattern",
    "process_with_status",
    "prompts",
    "protocols",
    "r",
    "refresh_token_if_needed",
    "risky_operation",
    "s",
    "save_config_command",
    "save_deployment_config",
    "save_user_preferences",
    "select_environment",
    "show_common_cli_params",
    "show_config_locations",
    "show_directory_tree",
    "show_environment_variables",
    "show_session_info",
    "stream_large_file",
    "t",
    "test_cli_command",
    "test_error_scenarios",
    "test_file_operations",
    "test_integration",
    "test_interactive_command",
    "typings",
    "u",
    "utilities",
    "validate_and_import_data",
    "validate_and_transform_data",
    "validate_app_config",
    "validate_business_rules",
    "validate_current_token",
    "validate_email_input",
    "validate_required_fields",
    "validate_user_credentials",
    "x",
    "your_cli_function",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
