# FLEXT-CLI Transformation Plan

**Transform to Generic, Complete CLI Foundation Library**

**Version**: 1.0
**Status**: IN PROGRESS (Phase 1: Architecture Foundation)
**Last Updated**: 2025-10-01
**Authority**: CLI Foundation Development

---

## 🎯 TRANSFORMATION GOALS

### Current State

- **30% functional** - Basic CLI with fragmented architecture
- Rich imports scattered in output.py only
- No Click imports (zero tolerance maintained)
- Basic file operations, prompts, and commands

### Target State

- **75%+ functional** - Complete, generic CLI foundation
- Proper abstraction layers (cli.py for Click, formatters.py for Rich)
- Comprehensive feature coverage across click, rich, and tabulate
- Production-ready with testing support

### Core Objectives

1. **Generic & Complete** - Maximum click, rich, tabulate functionality wrapped
2. **Simplified Usage** - Clean APIs following Flext standards
3. **Zero Limitations** - Comprehensive feature coverage without restrictions
4. **Ecosystem Friendly** - Maintains ZERO TOLERANCE (no direct click/rich imports)
5. **Backward Compatible** - All existing APIs continue working

---

## 📊 CURRENT STATE ANALYSIS

### What Exists ✅

- **FlextCliOutput** - Rich tables, progress, JSON/YAML/CSV/tree formatting
- **FlextCliFileTools** - Comprehensive file operations (1539 lines):
  - JSON, YAML, CSV, TSV, XML, TOML
  - Excel, Parquet formats
  - Zip archives, temp files
  - File hashing and permissions
  - File search and operations
- **FlextCliPrompts** - Text prompts, confirmation, choice, password, progress
- **FlextCliCommands** - Command registration and execution
- **Auth/Cmd/Debug** - Command groups
- **Rich imports** - ONLY in output.py ✅ (proper containment)
- **Click imports** - NONE ✅ (zero tolerance maintained)

### What's Missing ❌

1. **Architecture** - No proper abstraction layers:
   - ❌ cli.py (Click abstraction) - MISSING
   - ❌ formatters.py (Rich abstraction) - MISSING
   - ❌ main.py (Command system) - MISSING

2. **Click Wrapper** - No decorator builders, parameter types, context management

3. **Rich Features** - Missing:
   - Panels and bordered containers
   - Layouts (rows, columns, splits)
   - Live displays (real-time updates)
   - Spinners and status indicators
   - Markdown rendering
   - Syntax highlighting
   - Enhanced tracebacks

4. **Tabulate** - Not integrated (should be lightweight table alternative)

5. **Interactive** - Missing:
   - Multi-select lists
   - Autocomplete input
   - Fuzzy search
   - Form builders
   - Wizard workflows
   - File/directory pickers

6. **CLI Patterns** - No plugins, middleware, hooks system

7. **Validation** - Limited input validation and schema support

8. **Error Display** - Need Rich traceback formatting

---

## 🏗️ ARCHITECTURE TRANSFORMATION

### Current Structure (Monolithic)

```
src/flext_cli/
├── api.py (FlextCli facade)
├── output.py (Rich imports + formatting - MIXED CONCERNS)
├── file_tools.py (comprehensive - 1539 lines)
├── prompts.py (interactive - 650 lines)
├── commands.py (Click group wrapper)
├── auth.py, cmd.py, debug.py (command groups)
└── ... (supporting modules)
```

**Issues:**

- Rich functionality mixed in output.py
- No Click abstraction layer
- No command registration system
- Monolithic design

### Target Structure (Proper Abstraction Layers)

```
src/flext_cli/
├── api.py              # PUBLIC API - FlextCli facade (enhanced)
├── cli.py              # NEW ✅ - Click abstraction (ONLY file with click imports)
├── formatters.py       # NEW ✅ - Rich abstraction (dedicated Rich wrapper)
├── tables.py           # NEW - Tabulate integration
├── main.py             # NEW - FlextCliMain command system
├── output.py           # REFACTORED - High-level output API (uses formatters.py)
├── file_tools.py       # ENHANCED - Advanced file operations
├── prompts.py          # ENHANCED - Interactive features
├── commands.py         # ENHANCED - Command patterns
├── validators.py       # NEW - Input validation
├── decorators.py       # NEW - CLI decorators
├── plugins.py          # NEW - Plugin system
├── middleware.py       # NEW - Command middleware
├── hooks.py            # NEW - Lifecycle hooks
├── testing.py          # NEW - CLI testing helpers
└── ... (existing modules)
```

**Benefits:**

- Clear separation of concerns
- ZERO TOLERANCE enforcement (cli.py = Click, formatters.py = Rich)
- Extensible architecture
- Professional organization

---

## 📦 PHASE-BY-PHASE IMPLEMENTATION

### **PHASE 1: Architecture Foundation** ✅ IN PROGRESS

**Priority**: HIGH
**Status**: 2/7 complete
**Goal**: Proper abstraction layers with zero tolerance enforcement

#### 1.1 Create `cli.py` - Click Abstraction Layer ✅ COMPLETED

**Status**: ✅ COMPLETED (~660 lines)
**File**: `src/flext_cli/cli.py`

**ONLY file allowed to import Click in entire ecosystem**

**Implemented Features:**

- ✅ Decorator builders: `create_command_decorator()`, `create_group_decorator()`
- ✅ Parameter decorators: `create_option_decorator()`, `create_argument_decorator()`
- ✅ Parameter types:
  - `get_choice_type()` - Choice selections
  - `get_path_type()` - Path validation
  - `get_file_type()` - File handling
  - `get_int_range_type()` - Integer ranges
  - `get_float_range_type()` - Float ranges
- ✅ Context management:
  - `get_current_context()` - Access Click context
  - `create_pass_context_decorator()` - Context passing
- ✅ Command execution:
  - `echo()` - Console output
  - `confirm()` - User confirmation
  - `prompt()` - User input
- ✅ Testing support:
  - `create_cli_runner()` - CliRunner for testing
- ✅ Utilities:
  - `format_filename()` - Filename formatting
  - `get_terminal_size()` - Terminal dimensions
  - `clear_screen()` - Clear console
  - `pause()` - Wait for keypress

**Pattern:**

```python
from flext_cli import FlextCli

cli = FlextCli()
click_wrapper = cli.click()

# Create command decorator
cmd_result = click_wrapper.create_command_decorator(name="greet", help="Greet user")
if cmd_result.is_success:
    command = cmd_result.unwrap()

    @command
    def greet():
        click_wrapper.echo("Hello!")
```

**Quality Metrics:**

- ✅ FlextResult-based APIs throughout
- ✅ Comprehensive type hints
- ✅ Google-style docstrings
- ✅ Professional error handling
- ⚠️ Some linting warnings (FBT, ANN401) - expected for Click API wrapping

#### 1.2 Create `formatters.py` - Rich Abstraction Layer ✅ COMPLETED

**Status**: ✅ COMPLETED (~930 lines)
**File**: `src/flext_cli/formatters.py`

**ONLY file for Rich imports (besides output.py during transition)**

**Implemented Features:**

**Console Operations:**

- ✅ `print()` - Rich console print with full styling options
- ✅ `get_console()` - Console instance access
- ✅ `clear()` - Clear console

**Panels:**

- ✅ `create_panel()` - Bordered content containers
- ✅ `display_panel()` - Create and display panel

**Layouts:**

- ✅ `create_layout()` - Complex layout arrangements
- Support for rows, columns, splits

**Live Displays:**

- ✅ `create_live_display()` - Real-time updating displays

**Spinners & Status:**

- ✅ `create_spinner()` - Loading spinners
- ✅ `create_status()` - Status with spinner

**Progress Bars:**

- ✅ `create_progress()` - Progress bars with custom columns
- Support for multiple task tracking

**Markdown:**

- ✅ `render_markdown()` - Markdown rendering
- ✅ `display_markdown()` - Render and display markdown

**Syntax Highlighting:**

- ✅ `highlight_code()` - Code syntax highlighting
- ✅ `display_code()` - Highlight and display code
- Support for multiple languages and themes

**Rules & Dividers:**

- ✅ `create_rule()` - Section dividers
- ✅ `display_rule()` - Create and display rule

**Text Styling:**

- ✅ `create_text()` - Styled text objects
- ✅ `align_text()` - Text alignment

**Tables & Trees:**

- ✅ `create_table()` - Rich tables
- ✅ `create_tree()` - Tree structures

**Traceback Formatting:**

- ✅ `format_exception()` - Rich exception tracebacks

**Pattern:**

```python
from flext_cli import FlextCli

cli = FlextCli()
formatters = cli.formatters()

# Create panel
panel_result = formatters.create_panel(
    "Important Message",
    title="Alert",
    border_style="red bold"
)

# Render markdown
md_result = formatters.render_markdown("# Title\n\n**Bold** text")

# Syntax highlighting
code_result = formatters.highlight_code(
    "def hello(): print('hi')",
    language="python",
    line_numbers=True
)
```

**Quality Metrics:**

- ✅ FlextResult-based APIs throughout
- ✅ Comprehensive type hints
- ✅ Google-style docstrings
- ✅ Professional error handling
- ⚠️ Some linting warnings (FBT, D301) - expected for Rich API wrapping

#### 1.3 Create `tables.py` - Tabulate Integration 🔄 IN PROGRESS

**Status**: 🔄 IN PROGRESS
**File**: `src/flext_cli/tables.py`

**Lightweight alternative to Rich tables**

**Planned Features:**

- Simple ASCII tables for performance
- Multiple formats: plain, simple, grid, fancy_grid, pipe, orgtbl, rst, mediawiki, HTML, latex
- Optimized for large datasets
- No ANSI codes (plain text friendly)
- Automatic type detection and formatting
- Custom alignment per column

**Pattern:**

```python
from flext_cli import FlextCli

cli = FlextCli()
tables = cli.tables()

data = [
    {"name": "Alice", "age": 30, "city": "NYC"},
    {"name": "Bob", "age": 25, "city": "LA"}
]

# Rich table (visual, from formatters.py)
cli.formatters().create_table(data, show_lines=True)

# Tabulate table (plain text, faster)
tables.create_table(data, format="grid")  # ASCII grid
tables.create_table(data, format="pipe")  # Markdown pipe
tables.create_table(data, format="simple")  # Simple format
```

#### 1.4 Create `main.py` - Command Registration System ⏳ PENDING

**Status**: ⏳ PENDING
**File**: `src/flext_cli/main.py`

**Planned Features:**

- Command registration and discovery
- Command group management
- Plugin command loading
- Command metadata and documentation
- Command lifecycle management

#### 1.5 Refactor `output.py` ⏳ PENDING

**Status**: ⏳ PENDING
**File**: `src/flext_cli/output.py`

**Changes:**

- Remove Rich imports (move to formatters.py)
- Use formatters.py for all Rich functionality
- Maintain backward compatibility
- Add convenience methods for new features
- Delegate to formatters.py internally

#### 1.6 Update `api.py` Facade ⏳ PENDING

**Status**: ⏳ PENDING
**File**: `src/flext_cli/api.py`

**New Methods to Add:**

```python
class FlextCli:
    def click(self) -> FlextCliClick:
        """Access Click abstraction layer."""

    def formatters(self) -> FlextCliFormatters:
        """Access Rich formatters."""

    def tables(self) -> FlextCliTables:
        """Access Tabulate integration."""

    def main(self) -> FlextCliMain:
        """Access command registration system."""

    # Decorator shortcuts
    def command(self, *args, **kwargs):
        """Shortcut for creating commands."""

    def option(self, *args, **kwargs):
        """Shortcut for creating options."""

    def argument(self, *args, **kwargs):
        """Shortcut for creating arguments."""
```

#### 1.7 Phase 1 Validation ⏳ PENDING

**Validation Checklist:**

- [ ] `ruff check src/flext_cli/` - Zero violations
- [ ] `make type-check` - Zero errors in src/
- [ ] `make test` - All tests pass
- [ ] `make validate` - Complete pipeline passes
- [ ] Manual testing of new APIs
- [ ] Backward compatibility verified

---

### **PHASE 2: Click Complete Wrapper** ⏳ PENDING

**Priority**: HIGH
**Status**: NOT STARTED
**Goal**: 100% Click functionality available through flext-cli

**NOTE**: Phase 1.1 already provides comprehensive Click wrapper. This phase focuses on:

- Adding missing Click features
- Testing utilities
- Documentation and examples

#### 2.1 Decorator System Enhancement

**Current Status**: Basic decorators implemented in cli.py
**Needs**: Documentation, examples, ecosystem usage patterns

#### 2.2 Parameter Types Completion

**Implemented**: Choice, Path, File, IntRange, FloatRange
**Missing**: DateTime, UUID, Tuple types

#### 2.3 Context Management Enhancement

**Implemented**: Basic context access
**Needs**: Context values, defaults, command invocation contexts

#### 2.4 Testing Support Enhancement

**Implemented**: CliRunner wrapper
**Needs**: Isolated filesystem, result inspection helpers

---

### **PHASE 3: Rich Maximum Features** ⏳ PENDING

**Priority**: HIGH
**Status**: NOT STARTED (but formatters.py provides foundation)
**Goal**: Expose comprehensive Rich capabilities

**NOTE**: Phase 1.2 (formatters.py) already provides:

- ✅ Panels, layouts, live displays
- ✅ Spinners, status, progress bars
- ✅ Markdown, syntax highlighting
- ✅ Rules, text styling, tables, trees
- ✅ Traceback formatting

**This phase focuses on:**

- Documentation and examples
- Integration with output.py
- Ecosystem usage patterns
- Performance optimization

---

### **PHASE 4: Interactive Enhancement** ⏳ PENDING

**Priority**: MEDIUM
**Status**: NOT STARTED
**Goal**: Comprehensive interactive CLI capabilities

#### 4.1 Expand `prompts.py`

**Current Features** (existing):

- Text prompts, confirmation, choice, password
- Basic progress bars

**New Features to Add:**

- Multi-select lists: `prompt_multi_select()`
- Autocomplete input: `prompt_autocomplete()`
- Fuzzy search selection: `prompt_fuzzy_search()`
- Form builders: `create_form()`
- Wizard workflows: `create_wizard()`
- Questionnaire system: `run_questionnaire()`
- File picker: `prompt_file_picker()`
- Directory picker: `prompt_directory_picker()`
- Date/time pickers: `prompt_date()`, `prompt_time()`
- Interactive trees: Expandable/collapsible navigation

**Example Usage:**

```python
from flext_cli import FlextCli

cli = FlextCli()
prompts = cli.prompts()

# Multi-select
selected = prompts.prompt_multi_select(
    "Select features:",
    choices=["Feature A", "Feature B", "Feature C"],
    min_selections=1
)

# Wizard
wizard = prompts.create_wizard(
    steps=[
        {"name": "name", "prompt": "Project name?"},
        {"name": "path", "prompt": "Install path?", "type": "path"},
        {"name": "confirm", "prompt": "Proceed?", "type": "confirm"}
    ]
)
answers = wizard.run()
```

---

### **PHASE 5: File Tools Advanced** ⏳ PENDING

**Priority**: MEDIUM
**Status**: NOT STARTED
**Goal**: Production-grade file operations

#### 5.1 Enhance `file_tools.py`

**Current Features** (existing - 1539 lines):

- ✅ JSON, YAML, CSV, TSV, XML, TOML, Excel, Parquet
- ✅ Text/binary file operations
- ✅ Zip archives
- ✅ Temp files
- ✅ File hashing (MD5, SHA256)
- ✅ File search and permissions

**New Features to Add:**

- Streaming: `stream_read()`, `stream_write()` - memory-efficient large files
- Watching: `watch_directory()` - real-time file system monitoring
- Diff: `diff_files()`, `diff_directories()` - file comparison
- Merge: `merge_files()`, `merge_directories()` - intelligent merging
- Backup: `create_backup()`, `restore_backup()` - versioned backups
- Compression: `compress()`, `decompress()` - gzip, bzip2, lzma, zstd
- Enhanced checksums: BLAKE2, SHA512
- Locking: `acquire_lock()`, `release_lock()` - file locking
- Atomic writes: `atomic_write()` - crash-safe writes
- Glob patterns: `glob_match()`, `glob_filter()` - pattern matching
- Tree operations: `copy_tree()`, `move_tree()`, `sync_trees()`

---

### **PHASE 6: Tabulate Integration** ⏳ PENDING

**Priority**: MEDIUM
**Status**: Partially covered in Phase 1.3
**Goal**: Complete tabulate integration with all formats

---

### **PHASE 7: CLI Patterns** ⏳ PENDING

**Priority**: LOW
**Status**: NOT STARTED
**Goal**: Advanced CLI architecture patterns

#### 7.1 Create `plugins.py` - Plugin System

#### 7.2 Create `middleware.py` - Command Middleware

#### 7.3 Create `hooks.py` - Lifecycle Hooks

#### 7.4 Create `decorators.py` - Utility Decorators

---

### **PHASE 8: Validation & Error Handling** ⏳ PENDING

**Priority**: LOW
**Status**: NOT STARTED
**Goal**: Professional CLI validation and errors

#### 8.1 Create `validators.py`

#### 8.2 Enhanced Error Display with Rich

---

### **PHASE 9: Testing Support** ⏳ PENDING

**Priority**: LOW
**Status**: NOT STARTED
**Goal**: First-class CLI testing

#### 9.1 Create `testing.py`

---

## ✅ QUALITY ASSURANCE

### Validation After Each Phase

```bash
# 1. Quick file validation
ruff check src/flext_cli/[changed_file].py

# 2. Type checking
make type-check

# 3. Linting
make lint

# 4. Tests
make test

# 5. Complete validation
make validate
```

### Coverage Requirements

- **Source code**: 75%+ test coverage
- **New functionality**: 80%+ coverage
- **Critical paths**: 90%+ coverage

### Standards Enforcement

- ✅ Zero Click imports outside cli.py
- ✅ Zero Rich imports outside formatters.py (and output.py temporarily)
- ✅ FlextResult for all operations
- ✅ Complete type hints
- ✅ Google-style docstrings
- ✅ Backward compatibility maintained

---

## 🎯 EXPECTED OUTCOMES

### Functional Coverage

- **Before**: 30% functional
- **After Phase 1**: 45% functional (architecture + foundational wrappers)
- **After Phase 3**: 65% functional (complete Rich/Click coverage)
- **Final Target**: 75%+ functional

### Capability Matrix

| Feature         | Before     | Phase 1     | Target                                                               |
| --------------- | ---------- | ----------- | -------------------------------------------------------------------- |
| Click wrapper   | ❌ None    | ✅ Complete | ✅ Complete (decorators, types, context)                             |
| Rich features   | ⚠️ Basic   | ✅ Complete | ✅ Comprehensive (panels, layouts, live, spinners, markdown, syntax) |
| Tabulate        | ❌ None    | 🔄 Progress | ✅ Full integration                                                  |
| Interactive     | ⚠️ Limited | ⚠️ Limited  | ✅ Advanced (multi-select, autocomplete, wizards, pickers)           |
| File operations | ✅ Good    | ✅ Good     | ✅ Production-grade (streaming, watching, diff, atomic)              |
| CLI patterns    | ❌ None    | ❌ None     | ✅ Plugins, middleware, hooks                                        |
| Validation      | ⚠️ Basic   | ⚠️ Basic    | ✅ Comprehensive validators                                          |
| Testing         | ⚠️ Limited | ⚠️ Better   | ✅ First-class test support                                          |

### Ecosystem Benefits

1. **Zero Direct Imports** - All 32+ ecosystem projects use flext-cli exclusively
2. **No Limitations** - Every Click/Rich/Tabulate feature available
3. **Simple APIs** - Consistent FlextResult patterns
4. **Production Ready** - Comprehensive file tools, validation, error handling
5. **Developer Friendly** - Testing support, plugins, decorators

---

## 📋 IMPLEMENTATION STATUS

### Overall Progress: 15% Complete

**Completed:**

- ✅ Phase 1.1: cli.py - Click abstraction layer (~660 lines)
- ✅ Phase 1.2: formatters.py - Rich abstraction layer (~930 lines)

**In Progress:**

- 🔄 Phase 1.3: tables.py - Tabulate integration

**Pending:**

- ⏳ Phase 1.4-1.7: Complete Phase 1 (Architecture Foundation)
- ⏳ Phase 2-9: All subsequent phases

### Execution Strategy

**Incremental, one module at a time, with validation after each change**

1. ✅ Phase 1: Architecture Foundation (HIGHEST PRIORITY)
2. ⏩ Phase 2: Click Complete Wrapper
3. ⏩ Phase 3: Rich Maximum Features
4. 🔜 Phase 4: Interactive Enhancement
5. 🔜 Phase 5: File Tools Advanced
6. 🔜 Phase 6: Tabulate Integration
7. 🔜 Phase 7: CLI Patterns
8. 🔜 Phase 8: Validation & Error Handling
9. 🔜 Phase 9: Testing Support

---

## 🚀 SUCCESS CRITERIA

### Phase 1 Success Criteria

- ✅ cli.py created with comprehensive Click wrapper
- ✅ formatters.py created with comprehensive Rich wrapper
- ⏳ tables.py created with tabulate integration
- ⏳ main.py created with command registration
- ⏳ output.py refactored to use formatters.py
- ⏳ api.py updated with new component access
- ⏳ Zero linting violations in new files
- ⏳ All tests pass
- ⏳ Backward compatibility maintained

### Final Success Criteria

- ✅ ZERO Click imports outside cli.py
- ✅ ZERO Rich imports outside formatters.py
- ✅ 75%+ test coverage
- ✅ Zero type errors in src/
- ✅ Zero lint violations in src/
- ✅ All existing APIs working (backward compatible)
- ✅ Comprehensive documentation
- ✅ All 32+ ecosystem projects can use enhanced features
- ✅ No direct click/rich/tabulate imports needed anywhere

---

## 📚 REFERENCES

- **Project Documentation**: [README.md](../README.md)
- **Development Guide**: [development.md](development.md)
- **API Reference**: [api-reference.md](api-reference.md)
- **FLEXT Standards**: [../CLAUDE.md](../CLAUDE.md)
- **Workspace Standards**: [../../CLAUDE.md](../../CLAUDE.md)

---

**Result**: flext-cli becomes the complete, generic, user-friendly CLI foundation for the entire FLEXT ecosystem!
