"""FLEXT CLI error string authorities."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliConstantsErrors:
    """Flat error-message constants authority."""

    ERR_UNKNOWN_ERROR: ClassVar[str] = "unknown error"
    ERR_ENSURE_DIR_FAILED: ClassVar[str] = "ensure_dir: {error}"
    ERR_ENSURE_DIR_GENERIC_FAILED: ClassVar[str] = "ensure_dir failed"
    ERR_ATOMIC_WRITE_TEXT_FILE_FAILED: ClassVar[str] = "atomic_write_text_file: {error}"
    ERR_TEXT_READ_FAILED: ClassVar[str] = "Text read failed: {error}"
    ERR_TEXT_WRITE_FAILED: ClassVar[str] = "Text write failed: {error}"
    ERR_CSV_WRITE_FAILED: ClassVar[str] = "CSV write failed: {error}"
    ERR_CSV_READ_FAILED: ClassVar[str] = "CSV read failed: {error}"
    ERR_BINARY_READ_FAILED: ClassVar[str] = "Binary read failed: {error}"
    ERR_BINARY_WRITE_FAILED: ClassVar[str] = "Binary write failed: {error}"
    ERR_FILE_COPY_FAILED: ClassVar[str] = "File copy failed: {error}"
    ERR_CREATE_PARENT_DIR_FAILED: ClassVar[str] = (
        "failed to create parent dir for {target_path}"
    )
    ERR_ENSURE_SYMLINK_FAILED: ClassVar[str] = (
        "failed to ensure symlink for {target_path}: {error}"
    )
    ERR_FILE_PATH_EMPTY: ClassVar[str] = "File path must be non-empty"
    ERR_AUTO_LOAD_FAILED: ClassVar[str] = "Auto load failed"
    ERR_FILE_DELETION_FAILED: ClassVar[str] = "File deletion failed: {error}"
    ERR_ATOMIC_DIRECTORY_READ_FAILED: ClassVar[str] = (
        "Atomic directory read failed: {error}"
    )
    ERR_ATOMIC_DIRECTORY_CREATE_FAILED: ClassVar[str] = (
        "Atomic directory create failed: {error}"
    )
    ERR_ATOMIC_DIRECTORY_DELETE_FAILED: ClassVar[str] = (
        "Atomic directory delete failed: {error}"
    )
    ERR_ATOMIC_DIRECTORY_PUBLISH_FAILED: ClassVar[str] = (
        "Atomic directory publish failed: {error}"
    )
    ERR_ATOMIC_DIRECTORY_PLAN_FAILED: ClassVar[str] = (
        "Atomic directory-chain plan failed: {error}"
    )
    ERR_ATOMIC_DIRECTORY_CHAIN_CREATE_FAILED: ClassVar[str] = (
        "Atomic directory-chain create failed: {error}"
    )
    ERR_ATOMIC_PHYSICAL_TREE_INVENTORY_FAILED: ClassVar[str] = (
        "Atomic physical-tree inventory failed: {error}"
    )
    ERR_ATOMIC_PHYSICAL_TREE_CLEANUP_FAILED: ClassVar[str] = (
        "Atomic physical-tree cleanup failed: {error}"
    )
    ERR_JSON_LOAD_FAILED: ClassVar[str] = "JSON load failed: {error}"

    ERR_INVALID_CREDENTIALS: ClassVar[str] = (
        "Invalid credentials: missing token or username/password"
    )
    ERR_AUTH_SAVE_FAILED: ClassVar[str] = "Failed to save token: {error}"
    ERR_AUTH_LOAD_FAILED: ClassVar[str] = "Failed to load token: {error}"
    ERR_AUTH_FILE_NOT_FOUND: ClassVar[str] = "Token file does not exist"
    ERR_INVALID_OUTPUT_FORMAT: ClassVar[str] = "Invalid output format: {format}"
    ERR_SETTINGS_INFO_FAILED: ClassVar[str] = "Settings info failed: {error}"

    CLI_PARAM_ERR_TRACE_REQUIRES_DEBUG: ClassVar[str] = (
        "Trace mode requires debug mode to be enabled"
    )
    CLI_PARAM_ERR_FIELD_NOT_FOUND_FMT: ClassVar[str] = (
        "Field '{field_name}' not found in CLI parameter registry"
    )
    CLI_PARAM_ERR_APPLY_FAILED_FMT: ClassVar[str] = (
        "Failed to apply CLI parameters: {error}"
    )
    CLI_PARAM_ERR_INVALID_WITH_VALID_FMT: ClassVar[str] = (
        "invalid {field_label}: {field_value}. valid: {valid_values}"
    )
    CLI_PARAM_ERR_INVALID_WITH_OPTIONS_FMT: ClassVar[str] = (
        "invalid {field_label}: {field_value}. valid options: {valid_values}"
    )

    ERR_SHOW_SETTINGS_FAILED: ClassVar[str] = "Show settings failed: {error}"

    VALIDATION_MSG_FIELD_CANNOT_BE_EMPTY: ClassVar[str] = "{field_name} cannot be empty"

    ERR_INVALID_CONFIRM_INPUT: ClassVar[str] = (
        "Invalid confirmation input - please enter yes or no"
    )
    ERR_USER_CANCELLED_CONFIRMATION: ClassVar[str] = "User cancelled confirmation"
    ERR_INPUT_STREAM_ENDED: ClassVar[str] = "Input stream ended"
    ERR_NO_CHOICES: ClassVar[str] = "No choices provided"
    ERR_INTERACTIVE_CHOICE_DISABLED: ClassVar[str] = (
        "Interactive mode disabled for choice prompt"
    )
    ERR_CHOICE_REQUIRED_FMT: ClassVar[str] = "Choice required. Options: {choices}"
    ERR_INVALID_CHOICE_FMT: ClassVar[str] = "Invalid choice: {choice}"
    ERR_INTERACTIVE_PASSWORD_DISABLED: ClassVar[str] = (
        "Interactive mode disabled for password prompt"
    )
    ERR_PASSWORD_TOO_SHORT_FMT: ClassVar[str] = (
        "Password too short: minimum {min_length} characters"
    )

    ERR_INVALID_COMMAND_NAME: ClassVar[str] = "Invalid command name"
    ERR_COMMAND_FAILED: ClassVar[str] = "Command failed"
    ERR_COMMAND_NOT_FOUND: ClassVar[str] = "Command not found: {name}"
    ERR_HANDLER_NOT_CALLABLE: ClassVar[str] = "Handler not callable for: {name}"
    ERR_COMMAND_EXECUTION_FAILED: ClassVar[str] = "Command execution failed: {error}"
    ERR_COMMAND_NAME_EMPTY: ClassVar[str] = "Command name must be non-empty string"
    ERR_CLI_DEFINITION_INVALID_MODEL: ClassVar[str] = (
        "command '{command}' model '{model}': {reason}"
    )
    ERR_CLI_DEFINITION_FIELD: ClassVar[str] = (
        "command '{command}' model '{model}' field '{field}': {reason}"
    )
    ERR_FIELD_DEFAULT_NOT_CLI_VALUE_FMT: ClassVar[str] = (
        "field '{field_name}' default {value!r} has no CLI option form"
    )


__all__: t.MutableSequenceOf[str] = ["FlextCliConstantsErrors"]
