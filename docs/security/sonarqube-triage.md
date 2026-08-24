# Triagem SonarCloud — flext-sh/flext-cli

Gerado do dump da plataforma SonarCloud (2026-08-06).

Bead: `mro-2wjm.1`

## Resumo

**86 issues** — BLOCKER 1, CRITICAL 24, MAJOR 35, MINOR 26
Tipos: VULNERABILITY 4, BUG 1, CODE_SMELL 81 · **Debt total: 516min**

| regra | issues |
|---|---|
| `python:S116` | 17 |
| `python:S3776` | 13 |
| `shelldre:S7688` | 12 |
| `python:S1192` | 9 |
| `python:S8997` | 7 |
| `python:S7504` | 5 |
| `python:S3358` | 3 |
| `python:S5754` | 2 |
| `githubactions:S8233` | 2 |
| `python:S5778` | 2 |

## Como usar

Cada issue traz a **mensagem do SonarQube** (descreve o problema e o impacto), o **código real** (linha `>>>`), o tipo e o effort estimado.
**Decisão**: `corrigir` / `falso-positivo` (marcar na plataforma com justificativa) / `risco-aceito`. Ordem: BLOCKER → CRITICAL → VULNERABILITY → MAJOR. CODE_SMELL em volume pede correção de padrão.

## Issues

### 1 · 🔴 BLOCKER · CODE_SMELL · `python:S3516`
**Local**: `src/flext_cli/_utilities/_files_parts/flextcliutilitiesfiles_part_01.py:36` · **Effort**: 2min

> Refactor this method to not always return the same value.

```python
       32      def files_delete(file_path: t.Cli.TextPath) -> p.Result[bool]:
       33          """Delete one file-system path using canonical error handling."""
       34          path = Path(file_path)
       35  
>>>    36          def _delete() -> bool:
       37              if not path.exists() and not path.is_symlink():
       38                  return True
       39              if path.is_dir() and not path.is_symlink():
       40                  shutil.rmtree(path)
```

**Decisão**:

### 2 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_cells.py:58` · **Effort**: 16min

> Define a constant instead of duplicating this literal "Value kind." 8 times.

```python
       54              str, m.Field(min_length=1, description="Formatted Excel reference.")
       55          ]
       56  
       57      class XlsxBlankValue(m.FrozenModel):
>>>    58          kind: Literal["blank"] = m.Field(default="blank", description="Value kind.")
       59  
       60      class XlsxTextValue(m.FrozenModel):
       61          kind: Literal["text"] = m.Field(default="text", description="Value kind.")
       62          value: str = m.Field(description="Cell text.")
```

**Decisão**:

### 3 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_rules.py:20` · **Effort**: 6min

> Define a constant instead of duplicating this literal "Format kind." 3 times.

```python
       16      # NOTE (multi-agent, mro-j2yt.1): visual styles and protection remain
       17      # orthogonal so style assignment cannot silently unlock cells.
       18      class XlsxContainsTextFormatPlan(m.FrozenModel):
       19          kind: Literal["contains_text"] = m.Field(
>>>    20              default="contains_text", description="Format kind."
       21          )
       22          area: FlextCliModelsXlsxCells.XlsxCellRange = m.Field(
       23              description="Formatted range."
       24          )
```

**Decisão**:

### 4 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_rules.py:23` · **Effort**: 6min

> Define a constant instead of duplicating this literal "Formatted range." 3 times.

```python
       19          kind: Literal["contains_text"] = m.Field(
       20              default="contains_text", description="Format kind."
       21          )
       22          area: FlextCliModelsXlsxCells.XlsxCellRange = m.Field(
>>>    23              description="Formatted range."
       24          )
       25          text: Annotated[str, m.Field(min_length=1, description="Searched text.")]
       26          style: Annotated[str, m.Field(min_length=1, description="Named style.")]
       27          stop_if_true: bool = m.Field(default=False, description="Stop later rules.")
```

**Decisão**:

### 5 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_rules.py:27` · **Effort**: 6min

> Define a constant instead of duplicating this literal "Stop later rules." 3 times.

```python
       23              description="Formatted range."
       24          )
       25          text: Annotated[str, m.Field(min_length=1, description="Searched text.")]
       26          style: Annotated[str, m.Field(min_length=1, description="Named style.")]
>>>    27          stop_if_true: bool = m.Field(default=False, description="Stop later rules.")
       28  
       29      class XlsxCellFormatPlan(m.FrozenModel):
       30          kind: Literal["cell"] = m.Field(default="cell", description="Format kind.")
       31          area: FlextCliModelsXlsxCells.XlsxCellRange = m.Field(
```

**Decisão**:

### 6 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_style_primitives.py:16` · **Effort**: 8min

> Define a constant instead of duplicating this literal "Color kind." 4 times.

```python
       12  
       13      # NOTE (multi-agent, mro-j2yt.1): optional values preserve the source
       14      # OOXML distinction between an absent attribute and an explicit false.
       15      class XlsxRgbColor(m.FrozenModel):
>>>    16          kind: Literal["rgb"] = m.Field(default="rgb", description="Color kind.")
       17          value: Annotated[
       18              str,
       19              m.Field(
       20                  pattern=r"^(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$",
```

**Decisão**:

### 7 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_validation.py:77` · **Effort**: 6min

> Define a constant instead of duplicating this literal "Rule kind." 3 times.

```python
       73          XlsxUnaryComparison | XlsxRangeComparison, m.Field(discriminator="mode")
       74      ]
       75  
       76      class XlsxListValidationPlan(m.FrozenModel):
>>>    77          kind: Literal["list"] = m.Field(default="list", description="Rule kind.")
       78          area: FlextCliModelsXlsxCells.XlsxCellRange = m.Field(
       79              description="Validated cell range."
       80          )
       81          source: FlextCliModelsXlsxValidation.XlsxListSource = m.Field(
```

**Decisão**:

### 8 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_validation.py:79` · **Effort**: 6min

> Define a constant instead of duplicating this literal "Validated cell range." 3 times.

```python
       75  
       76      class XlsxListValidationPlan(m.FrozenModel):
       77          kind: Literal["list"] = m.Field(default="list", description="Rule kind.")
       78          area: FlextCliModelsXlsxCells.XlsxCellRange = m.Field(
>>>    79              description="Validated cell range."
       80          )
       81          source: FlextCliModelsXlsxValidation.XlsxListSource = m.Field(
       82              description="Allowed-value source."
       83          )
```

**Decisão**:

### 9 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/_xlsx/xlsx_validation.py:85` · **Effort**: 6min

> Define a constant instead of duplicating this literal "Validation UI behavior." 3 times.

```python
       81          source: FlextCliModelsXlsxValidation.XlsxListSource = m.Field(
       82              description="Allowed-value source."
       83          )
       84          messages: FlextCliModelsXlsxValidation.XlsxValidationMessages = m.Field(
>>>    85              description="Validation UI behavior."
       86          )
       87  
       88      class XlsxComparisonValidationPlan(m.FrozenModel):
       89          kind: Literal["whole", "decimal", "date", "time", "text_length"] = m.Field(
```

**Decisão**:

### 10 · 🟠 CRITICAL · CODE_SMELL · `python:S1192`
**Local**: `src/flext_cli/_models/docx_styles.py:17` · **Effort**: 6min

> Define a constant instead of duplicating this literal "Color kind." 3 times.

```python
       13      # NOTE (multi-agent, mro-j2yt.1): style primitives are data-only and
       14      # carry no document-specific or customer policy.
       15  
       16      class DocxRgbColor(m.FrozenModel):
>>>    17          kind: Literal["rgb"] = m.Field(default="rgb", description="Color kind.")
       18          value: Annotated[
       19              str,
       20              m.Field(
       21                  pattern=r"^(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$",
```

**Decisão**:

### 11 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_01.py:29` · **Effort**: 17min

> Refactor this function to reduce its Cognitive Complexity from 27 to the 15 allowed.

```python
       25      """Implementation part for FlextCliUtilitiesFileTestHelpersMixin."""
       26  
       27      @classmethod
       28      @contextmanager
>>>    29      def files_context(
       30          cls,
       31          content: Mapping[str, str | bytes | t.JsonValue | t.SequenceOf[t.StrSequence]],
       32          *,
       33          directory: Path | None = None,
```

**Decisão**:

### 12 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_file_test_helper_parts/flextcliutilitiesfiletesthelpersmixin_part_02.py:22` · **Effort**: 9min

> Refactor this function to reduce its Cognitive Complexity from 19 to the 15 allowed.

```python
       18  class FlextCliUtilitiesFileTestHelpersMixin:
       19      """Implementation part for FlextCliUtilitiesFileTestHelpersMixin."""
       20  
       21      @staticmethod
>>>    22      def files_assert_exists(
       23          path: Path,
       24          *,
       25          is_file: bool | None = None,
       26          is_dir: bool | None = None,
```

**Decisão**:

### 13 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_rules/_loaders.py:88` · **Effort**: 28min

> Refactor this function to reduce its Cognitive Complexity from 38 to the 15 allowed.

```python
       84              f"Failed to load rules registry: no {registry_filename} found"
       85          )
       86  
       87      @classmethod
>>>    88      def rules_load_local_definitions[TRuleKind, TFileRuleKind](
       89          cls,
       90          config_path: Path,
       91          **kwargs: t.Cli.CliValue
       92          | Path
```

**Decisão**:

### 14 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_runtime_process_execution.py:35` · **Effort**: 16min

> Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.

```python
       31  ):
       32      """Own one child process and its streaming resources."""
       33  
       34      @classmethod
>>>    35      def _execute_streamed_process(
       36          cls,
       37          cmd: t.StrSequence,
       38          output_path: Path,
       39          cwd: t.Cli.TextPath | None,
```

**Decisão**:

### 15 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_runtime_process_monitor.py:21` · **Effort**: 17min

> Refactor this function to reduce its Cognitive Complexity from 27 to the 15 allowed.

```python
       17  ):
       18      """Monitor one process group through events and one absolute deadline."""
       19  
       20      @classmethod
>>>    21      def _monitor_process(
       22          cls,
       23          process: p.Cli.ProcessHandle,
       24          process_done: threading.Event,
       25          wake: threading.Event,
```

**Decisão**:

### 16 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_xlxx/xlsx_formula_codec.py:18` · **Effort**: 16min

> Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.

```python
       14      # it back. Authored formulas keep canonical names; this codec owns the
       15      # single storage transformation at the external write boundary and
       16      # never rewrites text inside string literals.
       17      @classmethod
>>>    18      def storage_formula(cls, formula: str) -> str:
       19          future = c.Cli.XLSX_FUTURE_FUNCTIONS
       20          prefix = c.Cli.XLSX_FUTURE_FUNCTION_PREFIX
       21          parts: list[str] = []
       22          index = 0
```

**Decisão**:

### 17 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_xlxx/xlsx_layout.py:30` · **Effort**: 22min

> Refactor this function to reduce its Cognitive Complexity from 32 to the 15 allowed.

```python
       26              detail = str(exc).strip() or exc.__class__.__name__
       27              return r[bool].fail(f"{c.Cli.XlsxError.RENDER_FAILED}: {detail}")
       28  
       29      @classmethod
>>>    30      def _apply_layout_unchecked(
       31          cls, worksheet: Worksheet, plan: m.Cli.XlsxSheetLayoutPlan
       32      ) -> p.Result[bool]:
       33          for item in plan.comments:
       34              comment = Comment(item.text, item.author)
```

**Decisão**:

### 18 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_xlxx/xlsx_recalc.py:77` · **Effort**: 6min

> Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

```python
       73              content = (output_dir / c.Cli.XLSX_RECALC_SOURCE_NAME).read_bytes()
       74          return r[m.Cli.XlsxRecalcResult].ok(m.Cli.XlsxRecalcResult(content=content))
       75  
       76      @classmethod
>>>    77      def xlsx_recalc_parity(
       78          cls, request: m.Cli.XlsxRecalcParityRequest
       79      ) -> p.Result[m.Cli.XlsxRecalcParityReport]:
       80          """Recalculate and compare cached values against source formulas."""
       81          formula_snapshot = cls.xlsx_snapshot(
```

**Decisão**:

### 19 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_xlxx/xlsx_recalc_evidence.py:30` · **Effort**: 6min

> Refactor this function to reduce its Cognitive Complexity from 16 to the 15 allowed.

```python
       26              raise ValueError(msg)
       27          return result.value
       28  
       29      @classmethod
>>>    30      def _worksheet_targets(
       31          cls, workbook_root: p.Cli.XlsxXmlElement, rels_root: p.Cli.XlsxXmlElement
       32      ) -> tuple[tuple[str, str], ...]:
       33          relationships: tuple[tuple[str, str], ...] = ()
       34          for relationship in rels_root.iter():
```

**Decisão**:

### 20 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_xlxx/xlsx_recalc_evidence.py:81` · **Effort**: 16min

> Refactor this function to reduce its Cognitive Complexity from 26 to the 15 allowed.

```python
       77              )
       78          return r[tuple[tuple[str, ...], tuple[str, ...]]].ok(evidence)
       79  
       80      @classmethod
>>>    81      def _formula_cache_evidence_unchecked(
       82          cls, source: bytes
       83      ) -> tuple[tuple[str, ...], tuple[str, ...]]:
       84          with ZipFile(BytesIO(source)) as archive:
       85              workbook_root = cls._require_xml(archive, c.Cli.XLSX_WORKBOOK_MEMBER)
```

**Decisão**:

### 21 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/_xlxx/xlsx_style_catalog.py:26` · **Effort**: 12min

> Refactor this function to reduce its Cognitive Complexity from 22 to the 15 allowed.

```python
       22          digest = sha256(repr(visual).encode("utf-8")).hexdigest()[:16]
       23          return f"{prefix}_{digest}"
       24  
       25      @classmethod
>>>    26      def _source_visuals(
       27          cls, source: bytes
       28      ) -> p.Result[tuple[m.Cli.XlsxSourceVisualStyle, ...]]:
       29          workbook_result = cls._load_workbook(source)
       30          if workbook_result.failure:
```

**Decisão**:

### 22 · 🟠 CRITICAL · CODE_SMELL · `python:S5754`
**Local**: `src/flext_cli/_utilities/framework.py:218` · **Effort**: 5min

> Reraise this exception to stop the application as the user expects

```python
      214          except typer.Exit as exc:
      215              if (failure := cls._active_failure.get()) is not None:
      216                  return r[bool].from_failure(failure)
      217              return cls._exit_code_result(exc.exit_code)
>>>   218          except SystemExit as exc:
      219              if (failure := cls._active_failure.get()) is not None:
      220                  return r[bool].from_failure(failure)
      221              exit_code = (
      222                  exc.code if isinstance(exc.code, int) else c.Cli.EXIT_CODE_FAILURE
```

**Decisão**:

### 23 · 🟠 CRITICAL · CODE_SMELL · `python:S5754`
**Local**: `src/flext_cli/_utilities/framework.py:267` · **Effort**: 5min

> Reraise this exception to stop the application as the user expects

```python
      263          except click.Abort as exc:
      264              return e.fail_operation(
      265                  c.Cli.OP_EXECUTE_APPLICATION, exc, result_type=r[bool]
      266              )
>>>   267          except SystemExit as exc:
      268              exit_code = (
      269                  exc.code if isinstance(exc.code, int) else c.Cli.EXIT_CODE_FAILURE
      270              )
      271              return cls._exit_code_result(exit_code)
```

**Decisão**:

### 24 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/pipeline.py:20` · **Effort**: 20min

> Refactor this function to reduce its Cognitive Complexity from 30 to the 15 allowed.

```python
       16  
       17      _pipeline_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)
       18  
       19      @staticmethod
>>>    20      def execute_pipeline(
       21          stages: t.SequenceOf[m.Cli.PipelineStageSpec],
       22          context: m.Cli.PipelineStageContext,
       23          *,
       24          fail_fast: bool = c.Cli.PIPELINE_DEFAULT_FAIL_FAST,
```

**Decisão**:

### 25 · 🟠 CRITICAL · CODE_SMELL · `python:S3776`
**Local**: `src/flext_cli/_utilities/template.py:90` · **Effort**: 8min

> Refactor this function to reduce its Cognitive Complexity from 18 to the 15 allowed.

```python
       86              op_name="template_render_to",
       87          )
       88  
       89      @staticmethod
>>>    90      def template_render_dir(
       91          templates_root: Path,
       92          output_root: Path,
       93          context: p.Model,
       94          entries: t.SequenceOf[m.Cli.TemplateRenderEntry],
```

**Decisão**:

### 26 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `.github/scripts/install-git-hooks.sh:55` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       51  _log "Installing Beads git hooks (chained) at ${WORKSPACE_ROOT}"
       52  bd hooks install --chain >/dev/null || fail "bd hooks install --chain failed"
       53  
       54  hook_path="$(git rev-parse --git-path hooks/prepare-commit-msg)"
>>>    55  [ -f "${hook_path}" ] || fail "prepare-commit-msg hook missing after bd hooks install"
       56  
       57  _log "Applying FLEXT agent-trailer guard to ${hook_path}"
       58  GUARD_TOKEN="BD_ALLOW_AGENT_COMMIT_TRAILERS" python3 - "${hook_path}" <<'PY'
       59  import os
```

**Decisão**:

### 27 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `.github/scripts/install-git-hooks.sh:104` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
      100  grep -q 'BD_ALLOW_AGENT_COMMIT_TRAILERS' "${hook_path}" \
      101  	|| fail "guard token missing after injection"
      102  grep -q 'bd hooks run prepare-commit-msg' "${hook_path}" \
      103  	|| fail "bd delegation missing; refusing to leave hook without beads integration"
>>>   104  [ -f "$(git rev-parse --git-path hooks/pre-commit)" ] \
      105  	|| fail "pre-commit hook missing after provisioning"
      106  [ -f "$(git rev-parse --git-path hooks/pre-push)" ] \
      107  	|| fail "pre-push hook missing after provisioning"
      108  
```

**Decisão**:

### 28 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `.github/scripts/install-git-hooks.sh:106` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
      102  grep -q 'bd hooks run prepare-commit-msg' "${hook_path}" \
      103  	|| fail "bd delegation missing; refusing to leave hook without beads integration"
      104  [ -f "$(git rev-parse --git-path hooks/pre-commit)" ] \
      105  	|| fail "pre-commit hook missing after provisioning"
>>>   106  [ -f "$(git rev-parse --git-path hooks/pre-push)" ] \
      107  	|| fail "pre-push hook missing after provisioning"
      108  
      109  echo "install-git-hooks: prepare-commit-msg guarded (BD_ALLOW_AGENT_COMMIT_TRAILERS opt-in)"
```

**Decisão**:

### 29 · 🟡 MAJOR · VULNERABILITY · `githubactions:S8264`
**Local**: `.github/workflows/docs.yml:18` · **Effort**: 5min

> Move this read permission from workflow level to job level.

```yaml
       14        - ".github/workflows/docs.yml"
       15    workflow_dispatch:
       16  
       17  permissions:
>>>    18    contents: read
       19    pages: write
       20    id-token: write
       21  
       22  concurrency:
```

**Decisão**:

### 30 · 🟡 MAJOR · VULNERABILITY · `githubactions:S8233`
**Local**: `.github/workflows/docs.yml:19` · **Effort**: 5min

> Move this write permission from workflow level to job level.

```yaml
       15    workflow_dispatch:
       16  
       17  permissions:
       18    contents: read
>>>    19    pages: write
       20    id-token: write
       21  
       22  concurrency:
       23    group: pages
```

**Decisão**:

### 31 · 🟡 MAJOR · VULNERABILITY · `githubactions:S8233`
**Local**: `.github/workflows/docs.yml:20` · **Effort**: 5min

> Move this write permission from workflow level to job level.

```yaml
       16  
       17  permissions:
       18    contents: read
       19    pages: write
>>>    20    id-token: write
       21  
       22  concurrency:
       23    group: pages
       24    cancel-in-progress: false
```

**Decisão**:

### 32 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/PHASE_1_DELETIONS.sh:12` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
        8  echo ""
        9  
       10  # Step 4: Delete validator.py (empty stub)
       11  echo "Step 4: Deleting validator.py..."
>>>    12  if [ -f "src/flext_cli/validator.py" ]; then
       13  	rm src/flext_cli/validator.py
       14  	echo "✓ Deleted src/flext_cli/validator.py"
       15  else
       16  	echo "⊘ File already deleted: src/flext_cli/validator.py"
```

**Decisão**:

### 33 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/PHASE_1_DELETIONS.sh:22` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       18  
       19  # Step 5: Delete auth.py (duplicate module)
       20  echo ""
       21  echo "Step 5: Deleting auth.py..."
>>>    22  if [ -f "src/flext_cli/auth.py" ]; then
       23  	rm src/flext_cli/auth.py
       24  	echo "✓ Deleted src/flext_cli/auth.py"
       25  else
       26  	echo "⊘ File already deleted: src/flext_cli/auth.py"
```

**Decisão**:

### 34 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/execute_phase_1.sh:17` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       13  echo "========================================="
       14  echo ""
       15  
       16  # Verify we're in the right directory
>>>    17  if [ ! -f "src/flext_cli/__init__.py" ]; then
       18  	echo "❌ Error: Not in flext-cli project root"
       19  	exit 1
       20  fi
       21  
```

**Decisão**:

### 35 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7677`
**Local**: `docs/refactoring/execute_phase_1.sh:18` · **Effort**: 5min

> Redirect this error message to stderr (>&2).

```bash
       14  echo ""
       15  
       16  # Verify we're in the right directory
       17  if [ ! -f "src/flext_cli/__init__.py" ]; then
>>>    18  	echo "❌ Error: Not in flext-cli project root"
       19  	exit 1
       20  fi
       21  
       22  echo "📍 Working Directory: ${PWD}"
```

**Decisão**:

### 36 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/execute_phase_1.sh:27` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       23  echo ""
       24  
       25  # Step 1: Delete validator.py
       26  echo "Step 1/4: Deleting validator.py..."
>>>    27  if [ -f "src/flext_cli/validator.py" ]; then
       28  	rm -v src/flext_cli/validator.py
       29  	echo "✅ validator.py deleted"
       30  else
       31  	echo "⊘ validator.py already deleted"
```

**Decisão**:

### 37 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/execute_phase_1.sh:37` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       33  echo ""
       34  
       35  # Step 2: Delete auth.py
       36  echo "Step 2/4: Deleting auth.py..."
>>>    37  if [ -f "src/flext_cli/auth.py" ]; then
       38  	rm -v src/flext_cli/auth.py
       39  	echo "✅ auth.py deleted"
       40  else
       41  	echo "⊘ auth.py already deleted"
```

**Decisão**:

### 38 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/execute_phase_1.sh:48` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       44  
       45  # Step 3: Move testing.py
       46  echo "Step 3/4: Moving testing.py to tests/fixtures/..."
       47  mkdir -p tests/fixtures
>>>    48  if [ -f "src/flext_cli/testing.py" ]; then
       49  	mv -v src/flext_cli/testing.py tests/fixtures/testing_utilities.py
       50  	echo "✅ testing.py moved to tests/fixtures/testing_utilities.py"
       51  else
       52  	echo "⊘ testing.py already moved"
```

**Decisão**:

### 39 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/execute_phase_1.sh:62` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       58  
       59  # Count how many files need updating
       60  affected_files=$(find tests -name "*.py" -type f -exec grep -l "from flext_cli import.*Test\|from flext_cli.testing" {} \; 2>/dev/null | wc -l) || true
       61  
>>>    62  if [ "${affected_files}" -gt 0 ]; then
       63  	echo "Found ${affected_files} test files with imports to update"
       64  
       65  	# Update FlextCliTesting imports
       66  	find tests -name "*.py" -type f -exec sed -i \
```

**Decisão**:

### 40 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/execute_phase_1.sh:100` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
       96  
       97  # Check no references remain
       98  echo "Checking for remaining references..."
       99  remaining_references=$(grep -r "from flext_cli.validator\|from flext_cli.auth\|from flext_cli.testing" src/ tests/ 2>/dev/null | grep -v "tests/fixtures/testing_utilities") || true
>>>   100  if [ -n "${remaining_references}" ]; then
      101  	echo "⚠️  WARNING: Found remaining references (review above)"
      102  	echo "${remaining_references}"
      103  else
      104  	echo "✅ No problematic references found"
```

**Decisão**:

### 41 · 🟡 MAJOR · CODE_SMELL · `shelldre:S7688`
**Local**: `docs/refactoring/execute_phase_1.sh:113` · **Effort**: 2min

> Use '[[' instead of '[' for conditional tests. The '[[' construct is safer and more feature-rich.

```bash
      109  echo "Running validation suite..."
      110  validation_output=$(make val 2>&1) || validation_status=$?
      111  validation_status=${validation_status:-0}
      112  echo "${validation_output}" | tail -20
>>>   113  if [ "${validation_status}" -eq 0 ]; then
      114  	echo ""
      115  	echo "✅ Validation passed"
      116  else
      117  	echo ""
```

**Decisão**:

### 42 · 🟡 MAJOR · CODE_SMELL · `python:S8786`
**Local**: `examples/constants.py:66` · **Effort**: 20min

> Simplify this regular expression to reduce its runtime, as it has super-linear performance due to backtracking.

```python
       62      EXAMPLE_TABLE_HEADERS_FIELD_VALUE: Final[t.Pair[str, str]] = ("Field", "Value")
       63      EXAMPLE_TABLE_HEADERS_SETTING_VALUE: Final[t.Pair[str, str]] = ("Setting", "Value")
       64  
       65      EXAMPLE_REGEX_EMAIL: Final[t.RegexPattern] = re.compile(
>>>    66          r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
       67      )
       68      EXAMPLE_REGEX_DOT: Final[t.RegexPattern] = re.compile(r"\.")
       69  
       70      EXAMPLE_DEFAULT_HOST: Final[str] = "localhost"
```

**Decisão**:

### 43 · 🟡 MAJOR · CODE_SMELL · `python:S108`
**Local**: `examples/ex_06_settings.py:157` · **Effort**: 5min

> Either remove or fill this block of code.

```python
      153              case c.DeploymentEnvironment.TESTING:
      154                  result["max_workers"] = c.EXAMPLE_TESTING_MAX_WORKERS
      155                  result["enable_metrics"] = False
      156              case _:
>>>   157                  pass
      158          return result
      159  
      160      @staticmethod
      161      def initialize_services(
```

**Decisão**:

### 44 · 🟡 MAJOR · VULNERABILITY · `text:S8565`
**Local**: `pyproject.toml:-` · **Effort**: 5min

> Dependency versions are not predictable if the lock file (uv.lock, poetry.lock, pdm.lock or pylock.toml) is missing.

**Decisão**:

### 45 · 🟡 MAJOR · CODE_SMELL · `python:S3358`
**Local**: `src/flext_cli/_models/_base/flextclimodelsbase_part_07.py:80` · **Effort**: 5min

> Extract this nested conditional expression into an independent statement.

```python
       76                  case c.Cli.TypeKind.DICT:
       77                      source_mapping = (
       78                          self.value
       79                          if isinstance(self.value, Mapping)
>>>    80                          else self.default
       81                          if isinstance(self.default, Mapping)
       82                          else None
       83                      )
       84                      resolved_value = (
```

**Decisão**:

### 46 · 🟡 MAJOR · CODE_SMELL · `python:S3358`
**Local**: `src/flext_cli/_utilities/_options_parts/flextcliutilitiesoptions_part_02.py:28` · **Effort**: 5min

> Extract this nested conditional expression into an independent statement.

```python
       24          default_factory = getattr(field_info, "default_factory", None)
       25          source_value = (
       26              getattr(settings, field_name)
       27              if settings is not None and hasattr(settings, field_name)
>>>    28              else default_factory()
       29              if callable(default_factory)
       30              else getattr(field_info, "default", None)
       31          )
       32          try:
```

**Decisão**:

### 47 · 🟡 MAJOR · CODE_SMELL · `python:S3358`
**Local**: `src/flext_cli/_utilities/_runtime_process_monitor.py:160` · **Effort**: 5min

> Extract this nested conditional expression into an independent statement.

```python
      156              force = forwarded_count >= force_after_signals
      157              forwarded_signal = (
      158                  signal_number
      159                  if forwarded_count == 0
>>>   160                  else signal.SIGKILL
      161                  if force
      162                  else signal.SIGTERM
      163              )
      164              cls._record_signal_error(
```

**Decisão**:

### 48 · 🟡 MAJOR · CODE_SMELL · `python:S8495`
**Local**: `src/flext_cli/_utilities/_runtime_process_resources.py:83` · **Effort**: 10min

> Refactor this function to always return tuples of the same length.

```python
       79              errors.append("process deadline expired before durable log flush")
       80          return tuple(errors)
       81  
       82      @staticmethod
>>>    83      def _close_process_resources(stack: contextlib.ExitStack) -> tuple[str, ...]:
       84          try:
       85              stack.close()
       86          except c.EXC_OS_VALUE as exc:
       87              return (f"process resource close error: {exc}",)
```

**Decisão**:

### 49 · 🟡 MAJOR · BUG · `python:S3699`
**Local**: `src/flext_cli/_utilities/output.py:111` · **Effort**: 5min

> Remove this use of the output from "flush"; "flush" doesn’t return anything.

```python
      107      def emit_raw(text: str) -> None:
      108          """Write raw text to stdout as one atomic block."""
      109          with FlextCliUtilitiesOutput._EMIT_LOCK:
      110              _ = sys.stdout.write(text)
>>>   111              _ = sys.stdout.flush()
      112  
      113      @classmethod
      114      def info(cls, msg: str) -> None:
      115          """Emit one canonical info line."""
```

**Decisão**:

### 50 · 🟡 MAJOR · CODE_SMELL · `python:S3985`
**Local**: `src/flext_cli/services/_cli_parts/flextclicli_part_01.py:19` · **Effort**: 2min

> Remove this unused private '_ModelCommand' class.

```python
       15  
       16  class FlextCliCli:
       17      """Implementation part for FlextCliCli."""
       18  
>>>    19      class _ModelCommand[M: t.Cli.ModelLike]:
       20          """Callable wrapper with explicit signature for Typer introspection.
       21  
       22          Note: __annotations__ uses MutableMapping[str, type] because Typer reads
       23          it via inspect at runtime. __call__ uses t.Scalar kwargs because Typer
```

**Decisão**:

### 51 · 🟡 MAJOR · CODE_SMELL · `python:S112`
**Local**: `src/flext_cli/services/_prompts_support.py:75` · **Effort**: 20min

> Replace this generic exception class with a more specific one.

```python
       71          )
       72          if guarded.success:
       73              return guarded
       74          exc = guarded.error or operation
>>>    75          self._fatal(operation, message, Exception(exc), consequence)
       76          return r[TResult].fail(error_format.format(error=exc))
       77  
       78      def _fatal(
       79          self, operation: str, message: str, exc: Exception, consequence: str
```

**Decisão**:

### 52 · 🟡 MAJOR · CODE_SMELL · `python:S5778`
**Local**: `tests/test_xlsx_render.py:88` · **Effort**: 5min

> Refactor this exception test to have only one invocation possibly throwing an exception.

```python
       84  
       85  
       86  def test_xlsx_datetime_rejects_unrepresentable_timezone() -> None:
       87      """XLSX ingress fails before vendor serialization for aware datetimes."""
>>>    88      with pytest.raises(ValueError, match="Input should not have timezone info"):
       89          m.Cli.XlsxDateTimeValue(value=dt.datetime(2026, 7, 13, tzinfo=dt.UTC))
       90  
       91  
       92  def test_xlsx_render_executes_typed_runtime_plan() -> None:
```

**Decisão**:

### 53 · 🟡 MAJOR · CODE_SMELL · `python:S8997`
**Local**: `tests/unit/test_config_engine.py:81` · **Effort**: 5min

> Use the "monkeypatch" fixture for temporary modifications instead of manually modifying global state.

```python
       77      def test_config_load_yaml_expands_env(self, tmp_path: Path) -> None:
       78          """Verify that config load yaml expands env."""
       79          source = tmp_path / "app.yaml"
       80          source.write_text("path: ${CFG_ENGINE_HOME}/data\n", encoding="utf-8")
>>>    81          os.environ["CFG_ENGINE_HOME"] = "/eng"
       82          try:
       83              result = u.Cli.config_load(source)
       84          finally:
       85              os.environ.pop("CFG_ENGINE_HOME", None)
```

**Decisão**:

### 54 · 🟡 MAJOR · CODE_SMELL · `python:S8997`
**Local**: `tests/unit/test_env_expand_utilities.py:28` · **Effort**: 5min

> Use the "monkeypatch" fixture for temporary modifications instead of manually modifying global state.

```python
       24      """Interpolate ${VAR} / ${VAR:-default} templates through ``u.Cli``."""
       25  
       26      def test_env_expand_substitutes_braced_variable(self) -> None:
       27          """A ``${VAR}`` token is replaced by the process-environment value."""
>>>    28          os.environ["FLEXT_CLI_EXPAND_HOME"] = "/home/tester"
       29          try:
       30              result = u.Cli.env_expand("${FLEXT_CLI_EXPAND_HOME}/.claude")
       31          finally:
       32              os.environ.pop("FLEXT_CLI_EXPAND_HOME", None)
```

**Decisão**:

### 55 · 🟡 MAJOR · CODE_SMELL · `python:S8997`
**Local**: `tests/unit/test_env_expand_utilities.py:38` · **Effort**: 5min

> Use the "monkeypatch" fixture for temporary modifications instead of manually modifying global state.

```python
       34          tm.that(tm.ok(result), eq="/home/tester/.claude")
       35  
       36      def test_env_expand_substitutes_bare_variable(self) -> None:
       37          """A bare ``$VAR`` token is replaced by the process-environment value."""
>>>    38          os.environ["FLEXT_CLI_EXPAND_BARE"] = "/opt/x"
       39          try:
       40              result = u.Cli.env_expand("$FLEXT_CLI_EXPAND_BARE/bin")
       41          finally:
       42              os.environ.pop("FLEXT_CLI_EXPAND_BARE", None)
```

**Decisão**:

### 56 · 🟡 MAJOR · CODE_SMELL · `python:S8997`
**Local**: `tests/unit/test_env_expand_utilities.py:64` · **Effort**: 5min

> Use the "monkeypatch" fixture for temporary modifications instead of manually modifying global state.

```python
       60          tm.that(tm.ok(result), eq="prefix--suffix")
       61  
       62      def test_env_expand_template_is_data(self) -> None:
       63          """The template is a plain argument, so callers pass paths as data."""
>>>    64          os.environ["FLEXT_CLI_EXPAND_H"] = "/home/tester"
       65          try:
       66              for template, expected in (
       67                  (
       68                      "${FLEXT_CLI_EXPAND_H}/.codex/config.toml",
```

**Decisão**:

### 57 · 🟡 MAJOR · CODE_SMELL · `python:S8997`
**Local**: `tests/unit/test_env_utilities.py:28` · **Effort**: 5min

> Use the "monkeypatch" fixture for temporary modifications instead of manually modifying global state.

```python
       24  
       25      def test_env_read_returns_value_when_set(self) -> None:
       26          """A set environment variable is returned by name."""
       27          name = "FLEXT_CLI_ENV_READ_PROBE"
>>>    28          os.environ[name] = "probe-value"
       29          try:
       30              result = u.Cli.env_read(name)
       31          finally:
       32              os.environ.pop(name, None)
```

**Decisão**:

### 58 · 🟡 MAJOR · CODE_SMELL · `python:S8997`
**Local**: `tests/unit/test_env_utilities.py:49` · **Effort**: 5min

> Use the "monkeypatch" fixture for temporary modifications instead of manually modifying global state.

```python
       45      def test_env_read_name_is_data(self) -> None:
       46          """The variable name is a plain argument, so callers pass it as data."""
       47          first = "FLEXT_CLI_ENV_READ_A"
       48          second = "FLEXT_CLI_ENV_READ_B"
>>>    49          os.environ[first] = "value-a"
       50          os.environ[second] = "value-b"
       51          try:
       52              for name, expected in ((first, "value-a"), (second, "value-b")):
       53                  tm.that(tm.ok(u.Cli.env_read(name)), eq=expected)
```

**Decisão**:

### 59 · 🟡 MAJOR · CODE_SMELL · `python:S8997`
**Local**: `tests/unit/test_env_utilities.py:50` · **Effort**: 5min

> Use the "monkeypatch" fixture for temporary modifications instead of manually modifying global state.

```python
       46          """The variable name is a plain argument, so callers pass it as data."""
       47          first = "FLEXT_CLI_ENV_READ_A"
       48          second = "FLEXT_CLI_ENV_READ_B"
       49          os.environ[first] = "value-a"
>>>    50          os.environ[second] = "value-b"
       51          try:
       52              for name, expected in ((first, "value-a"), (second, "value-b")):
       53                  tm.that(tm.ok(u.Cli.env_read(name)), eq=expected)
       54          finally:
```

**Decisão**:

### 60 · 🟡 MAJOR · CODE_SMELL · `python:S5778`
**Local**: `tests/unit/test_model_commands_cov.py:90` · **Effort**: 5min

> Refactor this exception test to have only one invocation possibly throwing an exception.

```python
       86              command(name="invalid", value="not-an-int")
       87  
       88      def test_derive_model_rejects_missing_required_field(self) -> None:
       89          """Verify that derive model rejects missing required field."""
>>>    90          with pytest.raises(m.ValidationError):
       91              cli.derive_model(
       92                  m.Tests.ModelCommandSample, m.Tests.ModelCommandSource(value=1)
       93              )
       94  
```

**Decisão**:

### 61 · ⚪ MINOR · CODE_SMELL · `python:S7504`
**Local**: `conftest.py:21` · **Effort**: 5min

> Remove this unnecessary `list()` call on an already iterable object.

```python
       17          and Path(getattr(existing_package, "__file__", "")).resolve() == init_file
       18      ):
       19          return
       20  
>>>    21      for module_name in list(sys.modules):
       22          if module_name == package_name or module_name.startswith(f"{package_name}."):
       23              sys.modules.pop(module_name, None)
       24  
       25      package_spec = importlib.util.spec_from_file_location(
```

**Decisão**:

### 62 · ⚪ MINOR · CODE_SMELL · `shelldre:S1192`
**Local**: `docs/refactoring/execute_phase_1.sh:125` · **Effort**: 4min

> Define a constant instead of using the literal '=========================================' 6 times.

```bash
      121  
      122  # Summary
      123  echo "========================================="
      124  echo "Phase 1 Complete!"
>>>   125  echo "========================================="
      126  echo ""
      127  echo "📊 Summary:"
      128  echo "  • Files deleted: 2 (validator.py, auth.py)"
      129  echo "  • Files moved: 1 (testing.py → tests/fixtures/testing_utilities.py)"
```

**Decisão**:

### 63 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_constants/exceptions.py:52` · **Effort**: 2min

> Rename this field "YamlParseError" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       48      # ``type[<Class>]`` annotation. Widening to a generic exception hides
       49      # the real ``FlextBaseError.__init__`` (with **extra_kwargs) from pyrefly,
       50      # which then rejects ``command=``/``model=`` kwargs at raise sites
       51      # (validation.py).
>>>    52      YamlParseError: ClassVar[type[Exception]] = YAMLError
       53      YamlRoundtripError: ClassVar[type[Exception]] = RuamelYAMLError
       54      CliDefinitionError: ClassVar[type[CliDefinitionError]] = CliDefinitionError
       55      CliValidationError: ClassVar[type[CliValidationError]] = CliValidationError
       56  
```

**Decisão**:

### 64 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_constants/exceptions.py:53` · **Effort**: 2min

> Rename this field "YamlRoundtripError" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       49      # the real ``FlextBaseError.__init__`` (with **extra_kwargs) from pyrefly,
       50      # which then rejects ``command=``/``model=`` kwargs at raise sites
       51      # (validation.py).
       52      YamlParseError: ClassVar[type[Exception]] = YAMLError
>>>    53      YamlRoundtripError: ClassVar[type[Exception]] = RuamelYAMLError
       54      CliDefinitionError: ClassVar[type[CliDefinitionError]] = CliDefinitionError
       55      CliValidationError: ClassVar[type[CliValidationError]] = CliValidationError
       56  
       57  
```

**Decisão**:

### 65 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_constants/exceptions.py:54` · **Effort**: 2min

> Rename this field "CliDefinitionError" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       50      # which then rejects ``command=``/``model=`` kwargs at raise sites
       51      # (validation.py).
       52      YamlParseError: ClassVar[type[Exception]] = YAMLError
       53      YamlRoundtripError: ClassVar[type[Exception]] = RuamelYAMLError
>>>    54      CliDefinitionError: ClassVar[type[CliDefinitionError]] = CliDefinitionError
       55      CliValidationError: ClassVar[type[CliValidationError]] = CliValidationError
       56  
       57  
       58  __all__: list[str] = [
```

**Decisão**:

### 66 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_constants/exceptions.py:55` · **Effort**: 2min

> Rename this field "CliValidationError" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       51      # (validation.py).
       52      YamlParseError: ClassVar[type[Exception]] = YAMLError
       53      YamlRoundtripError: ClassVar[type[Exception]] = RuamelYAMLError
       54      CliDefinitionError: ClassVar[type[CliDefinitionError]] = CliDefinitionError
>>>    55      CliValidationError: ClassVar[type[CliValidationError]] = CliValidationError
       56  
       57  
       58  __all__: list[str] = [
       59      "CliDefinitionError",
```

**Decisão**:

### 67 · ⚪ MINOR · CODE_SMELL · `python:S7508`
**Local**: `src/flext_cli/_constants/settings.py:15` · **Effort**: 5min

> Remove this redundant call.

```python
       11  
       12  class FlextCliConstantsSettings:
       13      """CLI defaults, messages, registries, and output configuration."""
       14  
>>>    15      OUTPUT_FORMATS: ClassVar[t.StrSequence] = tuple(
       16          output_format.value for output_format in ce.OutputFormats
       17      )
       18      LOG_LEVELS: ClassVar[t.StrSequence] = tuple(item.value for item in c.LogLevel)
       19      MESSAGE_TYPES: ClassVar[t.StrSequence] = tuple(
```

**Decisão**:

### 68 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:25` · **Effort**: 2min

> Rename this field "Presentation" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       21  
       22      # NOTE (multi-agent, mro-j2yt.1): re-exporting keeps the external PPTX
       23      # dependency owned by flext-cli so cosmos-docgen can drop direct imports.
       24  
>>>    25      Presentation = staticmethod(_Presentation)
       26      PresentationDocument = PresentationDocument
       27      RGBColor = RGBColor
       28      MSO_SHAPE = MSO_SHAPE
       29      MSO_ANCHOR = MSO_ANCHOR
```

**Decisão**:

### 69 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:26` · **Effort**: 2min

> Rename this field "PresentationDocument" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       22      # NOTE (multi-agent, mro-j2yt.1): re-exporting keeps the external PPTX
       23      # dependency owned by flext-cli so cosmos-docgen can drop direct imports.
       24  
       25      Presentation = staticmethod(_Presentation)
>>>    26      PresentationDocument = PresentationDocument
       27      RGBColor = RGBColor
       28      MSO_SHAPE = MSO_SHAPE
       29      MSO_ANCHOR = MSO_ANCHOR
       30      MSO_AUTO_SIZE = MSO_AUTO_SIZE
```

**Decisão**:

### 70 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:27` · **Effort**: 2min

> Rename this field "RGBColor" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       23      # dependency owned by flext-cli so cosmos-docgen can drop direct imports.
       24  
       25      Presentation = staticmethod(_Presentation)
       26      PresentationDocument = PresentationDocument
>>>    27      RGBColor = RGBColor
       28      MSO_SHAPE = MSO_SHAPE
       29      MSO_ANCHOR = MSO_ANCHOR
       30      MSO_AUTO_SIZE = MSO_AUTO_SIZE
       31      PP_ALIGN = PP_ALIGN
```

**Decisão**:

### 71 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:33` · **Effort**: 2min

> Rename this field "BaseOxmlElement" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       29      MSO_ANCHOR = MSO_ANCHOR
       30      MSO_AUTO_SIZE = MSO_AUTO_SIZE
       31      PP_ALIGN = PP_ALIGN
       32      qn = staticmethod(_qn)
>>>    33      BaseOxmlElement = BaseOxmlElement
       34      Shape = Shape
       35      Picture = Picture
       36      Slide = Slide
       37      SlideLayout = SlideLayout
```

**Decisão**:

### 72 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:34` · **Effort**: 2min

> Rename this field "Shape" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       30      MSO_AUTO_SIZE = MSO_AUTO_SIZE
       31      PP_ALIGN = PP_ALIGN
       32      qn = staticmethod(_qn)
       33      BaseOxmlElement = BaseOxmlElement
>>>    34      Shape = Shape
       35      Picture = Picture
       36      Slide = Slide
       37      SlideLayout = SlideLayout
       38      TextFrame = TextFrame
```

**Decisão**:

### 73 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:35` · **Effort**: 2min

> Rename this field "Picture" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       31      PP_ALIGN = PP_ALIGN
       32      qn = staticmethod(_qn)
       33      BaseOxmlElement = BaseOxmlElement
       34      Shape = Shape
>>>    35      Picture = Picture
       36      Slide = Slide
       37      SlideLayout = SlideLayout
       38      TextFrame = TextFrame
       39      Emu = Emu
```

**Decisão**:

### 74 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:36` · **Effort**: 2min

> Rename this field "Slide" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       32      qn = staticmethod(_qn)
       33      BaseOxmlElement = BaseOxmlElement
       34      Shape = Shape
       35      Picture = Picture
>>>    36      Slide = Slide
       37      SlideLayout = SlideLayout
       38      TextFrame = TextFrame
       39      Emu = Emu
       40      Inches = Inches
```

**Decisão**:

### 75 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:37` · **Effort**: 2min

> Rename this field "SlideLayout" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       33      BaseOxmlElement = BaseOxmlElement
       34      Shape = Shape
       35      Picture = Picture
       36      Slide = Slide
>>>    37      SlideLayout = SlideLayout
       38      TextFrame = TextFrame
       39      Emu = Emu
       40      Inches = Inches
       41      Length = Length
```

**Decisão**:

### 76 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:38` · **Effort**: 2min

> Rename this field "TextFrame" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       34      Shape = Shape
       35      Picture = Picture
       36      Slide = Slide
       37      SlideLayout = SlideLayout
>>>    38      TextFrame = TextFrame
       39      Emu = Emu
       40      Inches = Inches
       41      Length = Length
       42      Pt = Pt
```

**Decisão**:

### 77 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:39` · **Effort**: 2min

> Rename this field "Emu" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       35      Picture = Picture
       36      Slide = Slide
       37      SlideLayout = SlideLayout
       38      TextFrame = TextFrame
>>>    39      Emu = Emu
       40      Inches = Inches
       41      Length = Length
       42      Pt = Pt
       43  
```

**Decisão**:

### 78 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:40` · **Effort**: 2min

> Rename this field "Inches" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       36      Slide = Slide
       37      SlideLayout = SlideLayout
       38      TextFrame = TextFrame
       39      Emu = Emu
>>>    40      Inches = Inches
       41      Length = Length
       42      Pt = Pt
       43  
       44  
```

**Decisão**:

### 79 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:41` · **Effort**: 2min

> Rename this field "Length" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       37      SlideLayout = SlideLayout
       38      TextFrame = TextFrame
       39      Emu = Emu
       40      Inches = Inches
>>>    41      Length = Length
       42      Pt = Pt
       43  
       44  
       45  __all__: tuple[str, ...] = ("FlextCliUtilitiesPptxTypes",)
```

**Decisão**:

### 80 · ⚪ MINOR · CODE_SMELL · `python:S116`
**Local**: `src/flext_cli/_utilities/_pptx/_types.py:42` · **Effort**: 2min

> Rename this field "Pt" to match the regular expression ^[_a-z][_a-z0-9]*$.

```python
       38      TextFrame = TextFrame
       39      Emu = Emu
       40      Inches = Inches
       41      Length = Length
>>>    42      Pt = Pt
       43  
       44  
       45  __all__: tuple[str, ...] = ("FlextCliUtilitiesPptxTypes",)
```

**Decisão**:

### 81 · ⚪ MINOR · CODE_SMELL · `python:S5713`
**Local**: `src/flext_cli/_utilities/_runtime_process_stream.py:81` · **Effort**: 1min

> Remove this redundant Exception class; it derives from another which is already caught.

```python
       77                  written = os.write(live_fd, remaining)
       78              except BlockingIOError:
       79                  stop.wait(cls._STREAM_POLL_SECONDS)
       80                  continue
>>>    81              except (BrokenPipeError, OSError, ValueError) as exc:
       82                  diagnostics.append(f"live output unavailable: {exc}")
       83                  return False
       84              if written <= 0:
       85                  diagnostics.append("live output write made no progress")
```

**Decisão**:

### 82 · ⚪ MINOR · CODE_SMELL · `python:S7504`
**Local**: `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_02.py:51` · **Effort**: 5min

> Remove this unnecessary `list()` call on an already iterable object.

```python
       47          Copying its entries into a single ``Table`` gives callers a normal,
       48          fully readable table without altering the source document.
       49          """
       50          table = tomlkit.table()
>>>    51          for entry_key in list(proxy):
       52              table[entry_key] = proxy[entry_key]
       53          return table
       54  
       55      @staticmethod
```

**Decisão**:

### 83 · ⚪ MINOR · CODE_SMELL · `python:S7504`
**Local**: `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_02.py:100` · **Effort**: 5min

> Remove this unnecessary `list()` call on an already iterable object.

```python
       96              # across the document. Consolidate them into one explicit table so
       97              # subsequent mutation targets a single contiguous section instead of
       98              # silently overwriting the fragments with an empty table.
       99              table = tomlkit.table()
>>>   100              for entry_key in list(existing):
      101                  table[entry_key] = existing[entry_key]
      102              del parent[key]
      103              parent[key] = table
      104              return table
```

**Decisão**:

### 84 · ⚪ MINOR · CODE_SMELL · `python:S7504`
**Local**: `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_02.py:111` · **Effort**: 5min

> Remove this unnecessary `list()` call on an already iterable object.

```python
      107              if not table.is_super_table():
      108                  return table
      109              del parent[key]
      110              table = tomlkit.table()
>>>   111              for entry_key in list(existing):
      112                  table[entry_key] = existing[entry_key]
      113              parent[key] = table
      114              return table
      115          table = tomlkit.table()
```

**Decisão**:

### 85 · ⚪ MINOR · CODE_SMELL · `python:S7504`
**Local**: `src/flext_cli/_utilities/_toml_parts/flextcliutilitiestoml_part_05.py:52` · **Effort**: 5min

> Remove this unnecessary `list()` call on an already iterable object.

```python
       48          }
       49          if current == normalized_expected:
       50              return False
       51          table = FlextCliUtilitiesTomlPart02.toml_ensure_table(container, key)
>>>    52          for existing_key in list(table):
       53              if existing_key not in normalized_expected:
       54                  del table[existing_key]
       55          for item_key, item_value in normalized_expected.items():
       56              table[item_key] = item_value
```

**Decisão**:

### 86 · ⚪ MINOR · CODE_SMELL · `python:S6353`
**Local**: `src/flext_cli/_utilities/env.py:10` · **Effort**: 5min

> Use concise character class syntax '\w' instead of '[A-Za-z0-9_]'.

```python
        6  import re
        7  
        8  from flext_cli import p, r
        9  
>>>    10  _VAR_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")
       11  
       12  
       13  class FlextCliUtilitiesEnv:
       14      """Read and interpolate environment variables, exposed on ``u.Cli``."""
```

**Decisão**:
