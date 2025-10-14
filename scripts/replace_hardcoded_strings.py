#!/usr/bin/env python3
"""Automated script to replace hardcoded strings with FlextCliConstants.

This script systematically replaces all hardcoded strings in the codebase
with their corresponding constant references.

ZERO TOLERANCE: No hardcoded strings allowed in src/.
"""

import re
from pathlib import Path

# Define replacement mappings: (pattern, replacement)
REPLACEMENTS = [
    # Error Messages
    (
        r'"Username and password are required"',
        "FlextCliConstants.ErrorMessages.USERNAME_PASSWORD_REQUIRED",
    ),
    (
        r'"Username must be at least 3 characters"',
        "FlextCliConstants.ErrorMessages.USERNAME_TOO_SHORT",
    ),
    (
        r'"Password must be at least 6 characters"',
        "FlextCliConstants.ErrorMessages.PASSWORD_TOO_SHORT",
    ),
    (r'"Token cannot be empty"', "FlextCliConstants.ErrorMessages.TOKEN_EMPTY"),
    (
        r'"Token file does not exist"',
        "FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND",
    ),
    (r'"Token file is empty"', "FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY"),
    (
        r'"Invalid credentials: missing token or username/password"',
        "FlextCliConstants.ErrorMessages.INVALID_CREDENTIALS",
    ),
    # File operation errors
    (
        r'f"Failed to save token: \{e\}"',
        "FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(error=e)",
    ),
    (
        r'f"Failed to load token: \{e\}"',
        "FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(error=e)",
    ),
    (
        r'f"Token paths failed: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.TOKEN_PATHS_FAILED.format(error=\1)",
    ),
    (
        r'f"Text file read failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.TEXT_FILE_READ_FAILED.format(error=e)",
    ),
    (
        r'f"Text file write failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.TEXT_FILE_WRITE_FAILED.format(error=e)",
    ),
    (
        r'f"File copy failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.FILE_COPY_FAILED.format(error=e)",
    ),
    (
        r'f"JSON write failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.JSON_WRITE_FAILED.format(error=e)",
    ),
    # Prompt errors
    (r'"No choices provided"', "FlextCliConstants.ErrorMessages.NO_CHOICES_PROVIDED"),
    (
        r'f"Invalid choice: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.INVALID_CHOICE.format(selected=\1)",
    ),
    (
        r'f"Text prompt failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.TEXT_PROMPT_FAILED.format(error=e)",
    ),
    (
        r'f"Confirmation prompt failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CONFIRMATION_PROMPT_FAILED.format(error=e)",
    ),
    (
        r'f"Choice prompt failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CHOICE_PROMPT_FAILED.format(error=e)",
    ),
    (
        r'f"Password prompt failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.PASSWORD_PROMPT_FAILED.format(error=e)",
    ),
    (
        r'"Interactive mode disabled and no default provided"',
        "FlextCliConstants.ErrorMessages.INTERACTIVE_MODE_DISABLED",
    ),
    (
        r'"Interactive mode disabled and no valid default provided"',
        "FlextCliConstants.ErrorMessages.INTERACTIVE_MODE_DISABLED_CHOICE",
    ),
    (
        r'"Interactive mode disabled for password input"',
        "FlextCliConstants.ErrorMessages.INTERACTIVE_MODE_DISABLED_PASSWORD",
    ),
    (
        r'f"Default value does not match required pattern: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.DEFAULT_PATTERN_MISMATCH.format(pattern=\1)",
    ),
    (
        r'f"Input does not match required pattern: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.INPUT_PATTERN_MISMATCH.format(pattern=\1)",
    ),
    (
        r'f"Password must be at least \{min_length\} characters"',
        "FlextCliConstants.ErrorMessages.PASSWORD_TOO_SHORT_MIN.format(min_length=min_length)",
    ),
    (
        r'f"History clear failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.HISTORY_CLEAR_FAILED.format(error=e)",
    ),
    # Config errors
    (
        r'f"Show config failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.SHOW_CONFIG_FAILED.format(error=e)",
    ),
    (
        r'f"Edit config failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.EDIT_CONFIG_FAILED.format(error=e)",
    ),
    (
        r'f"Config paths failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CONFIG_PATHS_FAILED.format(error=e)",
    ),
    (
        r'f"Config info failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CONFIG_INFO_FAILED.format(error=e)",
    ),
    (
        r'f"Failed to create default config: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.CREATE_DEFAULT_CONFIG_FAILED.format(error=\1)",
    ),
    (
        r'f"Failed to load config: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.LOAD_CONFIG_FAILED.format(error=\1)",
    ),
    (
        r'"Configuration data cannot be None"',
        "FlextCliConstants.ErrorMessages.CONFIG_DATA_NONE",
    ),
    (
        r'"Configuration data must be a dictionary"',
        "FlextCliConstants.ErrorMessages.CONFIG_DATA_NOT_DICT",
    ),
    (
        r'f"Config validation failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CONFIG_VALIDATION_FAILED.format(error=e)",
    ),
    # Output errors
    (
        r'"No data provided for table"',
        "FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED",
    ),
    (
        r'"Table format requires dict[str, object] or list of dicts"',
        "FlextCliConstants.ErrorMessages.TABLE_FORMAT_REQUIRED_DICT",
    ),
    (
        r'f"Unsupported format type: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT_TYPE.format(format_type=\1)",
    ),
    (
        r'f"Failed to create formatter: \{e\}"',
        "FlextCliConstants.ErrorMessages.CREATE_FORMATTER_FAILED.format(error=e)",
    ),
    (
        r'f"Failed to create Rich table: \{(\w+)\}"',
        r"FlextCliConstants.ErrorMessages.CREATE_RICH_TABLE_FAILED.format(error=\1)",
    ),
    # Log Messages - CAREFUL with string formatting
    (r'"Configuration displayed"', "FlextCliConstants.LogMessages.CONFIG_DISPLAYED"),
    (
        r'f"Config validation results: \{(\w+)\}"',
        r"FlextCliConstants.LogMessages.CONFIG_VALIDATION_RESULTS.format(results=\1)",
    ),
    (
        r'"Configuration edit completed successfully"',
        "FlextCliConstants.LogMessages.CONFIG_EDIT_COMPLETED",
    ),
    # Dict Keys - common dictionary keys
    (r'"token_file"', "FlextCliConstants.DictKeys.TOKEN_FILE"),
    (r'"refresh_token_file"', "FlextCliConstants.DictKeys.REFRESH_TOKEN_FILE"),
    (r'"token_path"', "FlextCliConstants.DictKeys.TOKEN_PATH"),
    (r'"refresh_token_path"', "FlextCliConstants.DictKeys.REFRESH_TOKEN_PATH"),
    (
        r'"token"(?!:)',
        "FlextCliConstants.DictKeys.TOKEN",
    ),  # Avoid replacing in JSON strings
    (r'"username"(?!:)', "FlextCliConstants.DictKeys.USERNAME"),
    (r'"password"(?!:)', "FlextCliConstants.DictKeys.PASSWORD"),
    (r'"authenticated"', "FlextCliConstants.DictKeys.AUTHENTICATED"),
    (r'"token_exists"', "FlextCliConstants.DictKeys.TOKEN_EXISTS"),
    (r'"refresh_token_exists"', "FlextCliConstants.DictKeys.REFRESH_TOKEN_EXISTS"),
    (r'"config_dir"', "FlextCliConstants.DictKeys.CONFIG_DIR"),
    (r'"config_exists"', "FlextCliConstants.DictKeys.CONFIG_EXISTS"),
    (r'"config_readable"', "FlextCliConstants.DictKeys.CONFIG_READABLE"),
    (r'"config_writable"', "FlextCliConstants.DictKeys.CONFIG_WRITABLE"),
    (r'"config"(?!:)', "FlextCliConstants.DictKeys.CONFIG"),
    (r'"logger_instance"', "FlextCliConstants.DictKeys.LOGGER_INSTANCE"),
    (r'"prompts_executed"', "FlextCliConstants.DictKeys.PROMPTS_EXECUTED"),
    (r'"interactive_mode"', "FlextCliConstants.DictKeys.INTERACTIVE_MODE"),
    (r'"host"(?!:)', "FlextCliConstants.DictKeys.HOST"),
    (r'"port"(?!:)', "FlextCliConstants.DictKeys.PORT"),
    # Encoding
    (r'"utf-8"', "FlextCliConstants.Encoding.UTF8"),
    # Yes/No Values
    (
        r'response\.lower\(\) in \{"y", "yes", "true", "1"\}',
        "response.lower() in FlextCliConstants.YesNo.YES_VALUES",
    ),
    (
        r'\.lower\(\) in \["y", "yes", "true", "1"\]',
        ".lower() in FlextCliConstants.YesNo.YES_VALUES",
    ),
    # Subdirectories
    (r'"config"(?= directory)', "FlextCliConstants.Subdirectories.CONFIG"),
    (r'"cache"(?= directory)', "FlextCliConstants.Subdirectories.CACHE"),
    (r'"logs"(?= directory)', "FlextCliConstants.Subdirectories.LOGS"),
    # Symbols
    (r'"✓"', "FlextCliConstants.Symbols.SUCCESS_MARK"),
    (r'"✗"', "FlextCliConstants.Symbols.FAILURE_MARK"),
    (r'f"❌ Error: \{(\w+)\}"', r'f"{FlextCliConstants.Symbols.ERROR_PREFIX} {\1}"'),
    (
        r'f"✅ Success: \{(\w+)\}"',
        r'f"{FlextCliConstants.Symbols.SUCCESS_PREFIX} {\1}"',
    ),
    # Status values
    (r'"simulated_input"', "FlextCliConstants.StatusValues.SIMULATED_INPUT"),
    (r'"\[password hidden\]"', "FlextCliConstants.StatusValues.PASSWORD_HIDDEN"),
    # JSON/YAML options
    (r'"skipkeys"', "FlextCliConstants.JsonOptions.SKIPKEYS"),
    (r'"ensure_ascii"', "FlextCliConstants.JsonOptions.ENSURE_ASCII"),
    (r'"check_circular"', "FlextCliConstants.JsonOptions.CHECK_CIRCULAR"),
    (r'"allow_nan"', "FlextCliConstants.JsonOptions.ALLOW_NAN"),
    (r'"cls"', "FlextCliConstants.JsonOptions.CLS"),
    (r'"indent"', "FlextCliConstants.JsonOptions.INDENT"),
    (r'"separators"', "FlextCliConstants.JsonOptions.SEPARATORS"),
    (r'"sort_keys"', "FlextCliConstants.JsonOptions.SORT_KEYS"),
    # Environment
    (
        r'"PYTEST_CURRENT_TEST"',
        "FlextCliConstants.EnvironmentConstants.PYTEST_CURRENT_TEST",
    ),
    (r'"pytest"(?! in)', "FlextCliConstants.EnvironmentConstants.PYTEST"),
    # Config files
    (r'"cli_config\.json"', "FlextCliConstants.ConfigFiles.CLI_CONFIG_JSON"),
    # Additional auth errors
    (r'"API key cannot be empty"', "FlextCliConstants.ErrorMessages.API_KEY_EMPTY"),
    (
        r'"Certificate file does not exist"',
        "FlextCliConstants.ErrorMessages.CERTIFICATE_NOT_EXIST",
    ),
    (
        r'f"Certificate authentication failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CERTIFICATE_AUTH_FAILED.format(error=e)",
    ),
    (
        r'"Hashed password cannot be empty"',
        "FlextCliConstants.ErrorMessages.HASHED_PASSWORD_EMPTY",
    ),
    (r'"Password cannot be empty"', "FlextCliConstants.ErrorMessages.PASSWORD_EMPTY"),
    (
        r'"Permission cannot be empty"',
        "FlextCliConstants.ErrorMessages.PERMISSION_EMPTY",
    ),
    (
        r'"Session ID cannot be empty"',
        "FlextCliConstants.ErrorMessages.SESSION_ID_EMPTY",
    ),
    (r'"User ID cannot be empty"', "FlextCliConstants.ErrorMessages.USER_ID_EMPTY"),
    (r'"User not found"', "FlextCliConstants.ErrorMessages.USER_NOT_FOUND"),
    (r'"Invalid token"', "FlextCliConstants.ErrorMessages.INVALID_TOKEN"),
    (
        r'f"Failed to store credentials: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_STORE_CREDENTIALS.format(error=e)",
    ),
    (
        r'f"Failed to hash password: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_HASH_PASSWORD.format(error=e)",
    ),
    (
        r'f"Failed to generate token: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_GENERATE_TOKEN.format(error=e)",
    ),
    (
        r'f"Failed to generate salt: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_GENERATE_SALT.format(error=e)",
    ),
    (
        r'f"Failed to clear credentials: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(error=e)",
    ),
    (
        r'f"Password verification failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_PASSWORD_VERIFICATION.format(error=e)",
    ),
    # Service messages
    (
        r'"FlextCliAuth service operational"',
        "FlextCliConstants.ServiceMessages.FLEXT_CLI_AUTH_OPERATIONAL",
    ),
    (
        r'"FlextCliDebug service operational"',
        "FlextCliConstants.ServiceMessages.FLEXT_CLI_DEBUG_OPERATIONAL",
    ),
    (
        r'"Configuration loaded successfully\. Use set_config_value to modify specific values\."',
        "FlextCliConstants.ServiceMessages.CONFIG_LOADED_SUCCESSFULLY",
    ),
    # Config errors
    (
        r'f"Business rules validation failed: \{validation_result\.error\}"',
        "FlextCliConstants.ErrorMessages.BUSINESS_RULES_VALIDATION_FAILED.format(error=validation_result.error)",
    ),
    (
        r'f"Cannot access config directory \{self\.config_dir\}: \{e\}"',
        "FlextCliConstants.ErrorMessages.CANNOT_ACCESS_CONFIG_DIR.format(config_dir=self.config_dir, error=e)",
    ),
    (
        r'f"Invalid output format: \{value\}"',
        "FlextCliConstants.ErrorMessages.INVALID_OUTPUT_FORMAT.format(format=value)",
    ),
    (
        r'f"Configuration file not found: \{config_file\}"',
        "FlextCliConstants.ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file=config_file)",
    ),
    (
        r'f"Unsupported configuration file format: \{config_file\.suffix\}"',
        "FlextCliConstants.ErrorMessages.UNSUPPORTED_CONFIG_FORMAT.format(suffix=config_file.suffix)",
    ),
    (
        r'f"Failed to load configuration from \{config_file\}: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_LOAD_CONFIG_FROM_FILE.format(file=config_file, error=e)",
    ),
    (
        r'f"Save failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.SAVE_FAILED.format(error=e)",
    ),
    (
        r'f"CLI args update failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CLI_ARGS_UPDATE_FAILED.format(error=e)",
    ),
    (
        r'f"Environment merge failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.ENV_MERGE_FAILED.format(error=e)",
    ),
    (
        r'f"Unknown config field: \{key\}"',
        "FlextCliConstants.ErrorMessages.UNKNOWN_CONFIG_FIELD.format(field=key)",
    ),
    (
        r'f"Invalid value for \{key\}: \{e\}"',
        "FlextCliConstants.ErrorMessages.INVALID_VALUE_FOR_FIELD.format(field=key, error=e)",
    ),
    (
        r"f\"Validation errors: \{'; '\.join\(errors\)\}\"",
        'FlextCliConstants.ErrorMessages.VALIDATION_ERRORS.format(errors="; ".join(errors))',
    ),
    (
        r'f"Config load failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CONFIG_LOAD_FAILED_MSG.format(error=e)",
    ),
    (
        r'f"Config save failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CONFIG_SAVE_FAILED_MSG.format(error=e)",
    ),
    # Validation messages (config.py)
    (
        r'f"Invalid output format: \{v\}\. Must be one of: \{valid_formats\}"',
        "FlextCliConstants.ValidationMessages.INVALID_OUTPUT_FORMAT_MUST_BE.format(format=v, valid_formats=valid_formats)",
    ),
    (
        r'"Profile name cannot be empty"',
        "FlextCliConstants.ValidationMessages.PROFILE_NAME_CANNOT_BE_EMPTY",
    ),
    (
        r'f"Invalid API URL format: \{v\}\. Must start with http:// or https://"',
        "FlextCliConstants.ValidationMessages.INVALID_API_URL_MUST_START.format(url=v)",
    ),
    (
        r"f\"Invalid log level: \{v\}\. Must be one of: \{', '\.join\(valid_levels\)\}\"",
        'FlextCliConstants.ValidationMessages.INVALID_LOG_LEVEL_MUST_BE.format(level=v, valid_levels=", ".join(valid_levels))',
    ),
    (
        r"f\"Invalid log verbosity: \{v\}\. Must be one of: \{', '\.join\(valid_verbosity\)\}\"",
        'FlextCliConstants.ValidationMessages.INVALID_LOG_VERBOSITY_MUST_BE.format(verbosity=v, valid_verbosity=", ".join(valid_verbosity))',
    ),
    # CLI/prompt errors
    (
        r'f"User aborted confirmation: \{e\}"',
        "FlextCliConstants.ErrorMessages.USER_ABORTED_CONFIRMATION.format(error=e)",
    ),
    (
        r'f"User aborted prompt: \{e\}"',
        "FlextCliConstants.ErrorMessages.USER_ABORTED_PROMPT.format(error=e)",
    ),
    # Command errors
    (
        r'f"Set config failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.SET_CONFIG_FAILED.format(error=e)",
    ),
    (
        r'f"Command registration failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.COMMAND_REGISTRATION_FAILED.format(error=e)",
    ),
    (
        r'f"Command not found: \{name\}"',
        "FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=name)",
    ),
    (
        r'f"Command not found: \{arg\}"',
        "FlextCliConstants.ErrorMessages.COMMAND_NOT_FOUND.format(name=arg)",
    ),
    (
        r'f"Command unregistration failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.COMMAND_UNREGISTRATION_FAILED.format(error=e)",
    ),
    (
        r'f"Group creation failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.GROUP_CREATION_FAILED.format(error=e)",
    ),
    (r'"CLI execution failed"', "FlextCliConstants.ErrorMessages.CLI_EXECUTION_FAILED"),
    (
        r'f"CLI execution failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CLI_EXECUTION_ERROR.format(error=e)",
    ),
    (
        r'f"Command execution failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e)",
    ),
    (
        r'f"Failed to clear commands: \{e\}"',
        "FlextCliConstants.ErrorMessages.COMMAND_EXECUTION_FAILED.format(error=e)",
    ),
    # Context errors
    (
        r'f"Context validation failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CONTEXT_VALIDATION_FAILED.format(error=e)",
    ),
    (
        r'f"Model attachment failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.MODEL_ATTACHMENT_FAILED.format(error=e)",
    ),
    (
        r'f"Model extraction failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.MODEL_EXTRACTION_FAILED.format(error=e)",
    ),
    # Core errors
    (
        r'"No active session to end"',
        "FlextCliConstants.ErrorMessages.NO_ACTIVE_SESSION",
    ),
    (
        r'f"Session end failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.SESSION_END_FAILED.format(error=e)",
    ),
    (
        r'f"Save configuration failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.SAVE_CONFIG_FAILED.format(error=e)",
    ),
    # Debug errors
    (
        r'f"Cannot write to current directory: \{e\}"',
        "FlextCliConstants.ErrorMessages.CANNOT_WRITE_CURRENT_DIR.format(error=e)",
    ),
    (
        r'f"Filesystem validation failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.FILESYSTEM_VALIDATION_FAILED.format(error=e)",
    ),
    # File tools errors
    (
        r'f"YAML write failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.YAML_WRITE_FAILED.format(error=e)",
    ),
    (
        r'"Format detection failed"',
        "FlextCliConstants.ErrorMessages.FORMAT_DETECTION_FAILED",
    ),
    (
        r'f"Unsupported format: \{file_format\}"',
        "FlextCliConstants.ErrorMessages.UNSUPPORTED_FORMAT.format(format=file_format)",
    ),
    # Plugin errors
    (
        r'f"Plugin directory does not exist: \{plugin_dir\}"',
        "FlextCliConstants.ErrorMessages.PLUGIN_DIR_NOT_EXIST.format(dir=plugin_dir)",
    ),
    (
        r'f"Plugin path is not a directory: \{plugin_dir\}"',
        "FlextCliConstants.ErrorMessages.PLUGIN_PATH_NOT_DIR.format(path=plugin_dir)",
    ),
    (
        r'f"Failed to discover plugins: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_DISCOVER_PLUGINS.format(error=e)",
    ),
    (
        r"f\"Plugin class '\{plugin_class_name\}' not found in module\"",
        "FlextCliConstants.ErrorMessages.PLUGIN_CLASS_NOT_FOUND.format(class_name=plugin_class_name)",
    ),
    (
        r"f\"No plugin class found in module '\{plugin_module\}'\"",
        "FlextCliConstants.ErrorMessages.NO_PLUGIN_CLASS_FOUND.format(module=plugin_module)",
    ),
    (
        r"f\"Failed to load plugin '\{plugin_module\}': \{e\}\"",
        "FlextCliConstants.ErrorMessages.FAILED_LOAD_PLUGIN.format(module=plugin_module, error=e)",
    ),
    (
        r'f"Plugin initialization failed: \{init_result\.error\}"',
        "FlextCliConstants.ErrorMessages.PLUGIN_INIT_FAILED.format(error=init_result.error)",
    ),
    (
        r'f"Plugin command registration failed: \{register_result\.error\}"',
        "FlextCliConstants.ErrorMessages.PLUGIN_REGISTER_FAILED.format(error=register_result.error)",
    ),
    (
        r'f"Failed to initialize plugin: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_INITIALIZE_PLUGIN.format(error=e)",
    ),
    (
        r'f"Load failed: \{load_result\.error\}"',
        "FlextCliConstants.ErrorMessages.LOAD_FAILED.format(error=load_result.error)",
    ),
    (
        r'f"Initialize failed: \{init_result\.error\}"',
        "FlextCliConstants.ErrorMessages.INITIALIZE_FAILED.format(error=init_result.error)",
    ),
    (
        r'f"Failed to load and initialize plugin: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_LOAD_AND_INIT_PLUGIN.format(error=e)",
    ),
    (
        r'f"Failed to get loaded plugins: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_GET_LOADED_PLUGINS.format(error=e)",
    ),
    (
        r'f"Failed to get initialized plugins: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_GET_INIT_PLUGINS.format(error=e)",
    ),
    (
        r'f"Failed to unload plugin: \{e\}"',
        "FlextCliConstants.ErrorMessages.FAILED_UNLOAD_PLUGIN.format(error=e)",
    ),
    # API errors
    (
        r'f"CLI configuration failed: \{e\}"',
        "FlextCliConstants.ErrorMessages.CLI_CONFIG_FAILED.format(error=e)",
    ),
]


def replace_strings_in_file(file_path: Path) -> tuple[int, int]:
    """Replace hardcoded strings in a single file.

    Returns:
        Tuple of (replacements_made, lines_changed)

    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        replacements_made = 0

        for pattern, replacement in REPLACEMENTS:
            before = content
            content = re.sub(pattern, replacement, content)
            if content != before:
                count = len(re.findall(pattern, before))
                replacements_made += count

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            lines_changed = len([
                line
                for line in content.split("\n")
                if line != original_content.split("\n")[content.split("\n").index(line)]
                if content.split("\n").index(line) < len(original_content.split("\n"))
            ])
            return (replacements_made, lines_changed)

        return (0, 0)

    except Exception:
        return (0, 0)


def main() -> None:
    """Main execution."""
    src_dir = Path(__file__).parent.parent / "src" / "flext_cli"

    # Files to process (excluding constants.py and __init__.py)
    py_files = [
        f
        for f in src_dir.glob("*.py")
        if f.name
        not in {"constants.py", "__init__.py", "core.py"}  # core.py already done
    ]

    total_replacements = 0
    total_files_modified = 0

    for py_file in sorted(py_files):
        replacements, _lines = replace_strings_in_file(py_file)

        if replacements > 0:
            total_replacements += replacements
            total_files_modified += 1


if __name__ == "__main__":
    main()
