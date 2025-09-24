"""CLI output and formatting tools."""

import csv
import json
from io import StringIO

import yaml
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table as RichTable
from rich.text import Text
from rich.tree import Tree
from tabulate import tabulate

from flext_core import FlextLogger, FlextResult, FlextService


class FlextCliOutput(FlextService[str]):
    """Comprehensive CLI output tools for the flext ecosystem.

    This class consolidates ALL CLI output functionality from:
    - flext_cli_formatters.py (Rich-based formatting with progress bars, trees)
    - utils.py FlextCliUtilities.Formatting (Basic format_json, format_yaml, format_csv)
    - Table formatting using tabulate library for clean, consistent output

    This is the ONLY module in FLEXT allowed to import Rich components directly.
    """

    def __init__(self) -> None:
        """Initialize CLI output with Rich console."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._console = Console()

    def execute(self) -> FlextResult[str]:
        """Execute the main domain service operation - required by FlextService."""
        return FlextResult[str].ok("FlextCliOutput operational")

    def format_data(
        self,
        data: object,
        format_type: str = "table",
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[str]:
        """Format data using specified format type.

        Args:
            data: Data to format
            format_type: Format type (table, json, yaml, csv, plain)
            title: Optional title for table format
            headers: Optional headers for table format

        Returns:
            FlextResult[str]: Formatted data string or error

        """
        match format_type.lower():
            case "json":
                return self.format_json(data)
            case "yaml":
                return self.format_yaml(data)
            case "table":
                # Convert object to appropriate type for format_table
                if isinstance(data, (dict, list)):
                    return self.format_table(data, title=title, headers=headers)
                return FlextResult[str].fail(
                    "Table format requires dict or list of dicts"
                )
            case "csv":
                return self.format_csv(data)
            case "plain":
                return FlextResult[str].ok(str(data))
            case _:
                return FlextResult[str].fail(f"Unsupported format type: {format_type}")

    def create_formatter(self, format_type: str) -> FlextResult[object]:
        """Create a formatter instance for the specified format type.

        Args:
            format_type: Format type to create formatter for

        Returns:
            FlextResult[object]: Formatter instance or error

        """
        try:
            # Validate format type is supported
            supported_formats = ["json", "yaml", "table", "csv", "plain"]
            if format_type.lower() not in supported_formats:
                return FlextResult[object].fail(
                    f"Unsupported format type: {format_type}"
                )

            # Return self as the formatter since this class handles all formats
            return FlextResult[object].ok(self)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to create formatter: {e}")

    def create_table(
        self,
        data: list[dict[str, object]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[RichTable]:
        """Create a Rich table from data.

        Args:
            data: List of dictionaries to display
            title: Optional table title
            headers: Optional custom headers

        Returns:
            FlextResult[RichTable]: Rich table object or error

        """
        if not data:
            return FlextResult[RichTable].fail("No data provided for table")

        try:
            table_headers = headers or list(data[0].keys())

            # Create Rich table
            table = RichTable(title=title or "")

            # Add columns
            for header in table_headers:
                table.add_column(str(header))

            # Add rows
            for row_data in data:
                row_values = [str(row_data.get(h, "")) for h in table_headers]
                table.add_row(*row_values)

            return FlextResult[RichTable].ok(table)

        except Exception as e:
            return FlextResult[RichTable].fail(f"Failed to create table: {e}")

    def table_to_string(
        self, table: RichTable, width: int | None = None
    ) -> FlextResult[str]:
        """Convert Rich table to string.

        Args:
            table: Rich table object
            width: Optional width for console

        Returns:
            FlextResult[str]: Table as string or error

        """
        try:
            console = Console(width=width)
            with console.capture() as capture:
                console.print(table)
            return FlextResult[str].ok(capture.get())
        except Exception as e:
            return FlextResult[str].fail(f"Failed to convert table to string: {e}")

    def create_progress_bar(
        self, description: str = "Processing...", total: int = 100
    ) -> FlextResult[tuple[Progress, TaskID]]:
        """Create a Rich progress bar.

        Args:
            description: Progress description
            total: Total number of steps

        Returns:
            FlextResult[tuple[Progress, TaskID]]: Progress and task ID or error

        """
        try:
            progress = Progress()
            task_id = progress.add_task(description, total=total)
            return FlextResult[tuple[Progress, TaskID]].ok((progress, task_id))
        except Exception as e:
            return FlextResult[tuple[Progress, TaskID]].fail(
                f"Failed to create progress bar: {e}"
            )

    def print_message(
        self, message: str, style: str = "", *, highlight: bool = False
    ) -> FlextResult[None]:
        """Print a message using Rich console.

        Args:
            message: Message to print
            style: Optional Rich style
            highlight: Whether to enable syntax highlighting

        Returns:
            FlextResult[None]: Success or failure result

        """
        try:
            if style:
                text = Text(message, style=style)
                self._console.print(text, highlight=highlight)
            else:
                self._console.print(message, highlight=highlight)
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Failed to print message: {e}")

    def print_error(self, message: str) -> FlextResult[None]:
        """Print an error message with red styling.

        Args:
            message: Error message to print

        Returns:
            FlextResult[None]: Success or failure result

        """
        return self.print_message(f"Error: {message}", style="bold red")

    def print_success(self, message: str) -> FlextResult[None]:
        """Print a success message with green styling.

        Args:
            message: Success message to print

        Returns:
            FlextResult[None]: Success or failure result

        """
        return self.print_message(f"Success: {message}", style="bold green")

    def print_warning(self, message: str) -> FlextResult[None]:
        """Print a warning message with yellow styling.

        Args:
            message: Warning message to print

        Returns:
            FlextResult[None]: Success or failure result

        """
        return self.print_message(f"Warning: {message}", style="bold yellow")

    def format_json(self, data: object) -> FlextResult[str]:
        """Format data as JSON.

        Args:
            data: Data to format

        Returns:
            FlextResult[str]: Formatted JSON string

        """
        try:
            return FlextResult[str].ok(json.dumps(data, default=str, indent=2))
        except Exception as e:
            return FlextResult[str].fail(f"JSON formatting failed: {e}")

    def format_yaml(self, data: object) -> FlextResult[str]:
        """Format data as YAML.

        Args:
            data: Data to format

        Returns:
            FlextResult[str]: Formatted YAML string

        """
        try:
            return FlextResult[str].ok(yaml.dump(data, default_flow_style=False))
        except Exception as e:
            return FlextResult[str].fail(f"YAML formatting failed: {e}")

    def format_csv(self, data: object) -> FlextResult[str]:
        """Format data as CSV.

        Args:
            data: Data to format

        Returns:
            FlextResult[str]: Formatted CSV string

        """
        try:
            if isinstance(data, list) and data and isinstance(data[0], dict):
                output = StringIO()
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                return FlextResult[str].ok(output.getvalue())
            if isinstance(data, dict):
                output = StringIO()
                fieldnames = list(data.keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
                return FlextResult[str].ok(output.getvalue())
            return FlextResult[str].ok(json.dumps(data, default=str, indent=2))
        except Exception as e:
            return FlextResult[str].fail(f"CSV formatting failed: {e}")

    def format_table(
        self,
        data: dict[str, object] | list[dict[str, object]],
        title: str | None = None,
        headers: list[str] | None = None,
    ) -> FlextResult[str]:
        """Format data as a tabulated table string.

        Args:
            data: Data to format (dict or list of dicts)
            title: Optional table title
            headers: Optional column headers

        Returns:
            FlextResult[str]: Table as string or error

        """
        try:
            if isinstance(data, dict):
                table_data: list[dict[str, object]] = [
                    {"Key": k, "Value": str(v)} for k, v in data.items()
                ]
                default_headers = ["Key", "Value"]
            else:
                table_data = data
                default_headers = list(table_data[0].keys()) if table_data else []

            columns = headers or default_headers

            # Convert data to list of lists for tabulate
            tabulate_data = []
            for row_data in table_data:
                row_values = [str(row_data.get(col, "")) for col in columns]
                tabulate_data.append(row_values)

            # Create table with tabulate
            table_str = tabulate(tabulate_data, headers=columns, tablefmt="grid")

            # Add title if provided
            if title:
                table_str = f"{title}\n{table_str}"

            return FlextResult[str].ok(table_str)

        except Exception as e:
            return FlextResult[str].fail(f"Failed to format table: {e}")

    def format_as_tree(
        self, data: dict[str, object], title: str = "Tree"
    ) -> FlextResult[str]:
        """Format hierarchical data as tree view.

        Args:
            data: Hierarchical data to format
            title: Tree title

        Returns:
            FlextResult[str]: Tree view as string

        """
        try:
            tree = Tree(title)
            self._build_tree(tree, data)

            with StringIO() as output:
                temp_console = Console(file=output, width=80)
                temp_console.print(tree)
                return FlextResult[str].ok(output.getvalue())

        except Exception as e:
            return FlextResult[str].fail(f"Failed to format tree: {e}")

    def _build_tree(self, tree: Tree, data: object) -> None:
        """Build tree recursively (helper for format_as_tree)."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    branch = tree.add(str(key))
                    self._build_tree(branch, value)
                elif isinstance(value, list):
                    branch = tree.add(f"{key} (list)")
                    for item in value:
                        self._build_tree(branch, item)
                else:
                    tree.add(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                self._build_tree(tree, item)
        else:
            tree.add(str(data))

    @property
    def console(self) -> Console:
        """Get Rich console instance.

        Returns:
            Console: Rich console instance

        """
        return self._console

    def get_console(self) -> Console:
        """Get the Rich console instance (method form).

        Returns:
            Console: Rich console instance

        """
        return self._console


__all__ = ["FlextCliOutput"]
