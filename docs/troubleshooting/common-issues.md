# Common Issues and Solutions

Este guia cobre os problemas mais comuns encontrados ao usar o FLEXT CLI e suas soluções.

## Installation Issues

### Poetry Installation Problems

**Problem**: Poetry não encontrado ou versão incorreta

```bash
$ poetry --version
poetry: command not found
```

**Solution**:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### Python Version Issues

**Problem**: Python 3.13+ não encontrado

```bash
$ python --version
Python 3.12.0
```

**Solutions**:

Using pyenv:

```bash
# Install Python 3.13
pyenv install 3.13.0
pyenv local 3.13.0

# Verify version
python --version
```

Using system package manager:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.13 python3.13-venv

# macOS with Homebrew
brew install python@3.13
```

### Dependency Installation Failures

**Problem**: Poetry install falha com conflitos de dependência

```bash
$ poetry install
The conflict is caused by:
  - flext-core depends on pydantic (>=2.11.7)
  - some-package depends on pydantic (<2.0.0)
```

**Solutions**:

```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Update lock file
poetry lock --no-update

# Force reinstall
poetry install --sync

# If still failing, recreate virtual environment
poetry env remove python
poetry install
```

## Import and Module Issues

### Circular Import Errors

**Problem**: Circular import quando importando flext-core

```bash
ImportError: cannot import name 'FlextOperationError' from partially initialized module 'flext_core.exceptions'
```

**Solutions**:

```bash
# Verify flext-core installation
cd ../flext-core
make install

# Check if flext-core is properly installed
poetry run python -c "import flext_core; print(flext_core.__version__)"

# Reinstall flext-cli dependencies
cd ../flext-cli
poetry install --sync
```

### Module Not Found Errors

**Problem**: Módulos não encontrados durante execução

```bash
ModuleNotFoundError: No module named 'flext_cli'
```

**Solutions**:

```bash
# Install in development mode
poetry install -e .

# Verify PYTHONPATH
echo $PYTHONPATH

# Check virtual environment
poetry env info

# Activate virtual environment manually
poetry shell
python -c "import flext_cli; print('OK')"
```

## CLI Execution Issues

### Command Not Found

**Problem**: Comando `flext` não encontrado após instalação

```bash
$ flext --help
flext: command not found
```

**Solutions**:

```bash
# Use Poetry to run
poetry run flext --help

# Install CLI globally
make install-cli

# Or install with pip
poetry build
pip install dist/*.whl

# Verify installation
which flext
flext --version
```

### Permission Errors

**Problem**: Problemas de permissão ao executar comandos

```bash
PermissionError: [Errno 13] Permission denied: '/usr/local/bin/flext'
```

**Solutions**:

```bash
# Use Poetry run instead of global install
poetry run flext --help

# Install in user directory
pip install --user dist/*.whl

# Fix permissions
sudo chmod +x /usr/local/bin/flext
```

## Configuration Issues

### Configuration File Not Found

**Problem**: Arquivo de configuração não encontrado

```bash
Configuration file not found: /home/user/.flx/config.yaml
```

**Solutions**:

```bash
# Create configuration directory
mkdir -p ~/.flx

# Create basic configuration
cat > ~/.flx/config.yaml << EOF
default:
  profile: development
  output_format: table
  debug: false
EOF

# Use environment variables instead
export FLEXT_CLI_CONFIG_PATH=/path/to/config.yaml
export FLX_PROFILE=development
```

### Invalid Configuration

**Problem**: Configuração inválida ou corrompida

```bash
Error: Invalid configuration format
```

**Solutions**:

```bash
# Validate YAML syntax
poetry run python -c "import yaml; yaml.safe_load(open('~/.flx/config.yaml'))"

# Reset to default configuration
rm ~/.flx/config.yaml
poetry run flext config show  # Will create default config

# Use debug mode to see configuration loading
poetry run flext --debug config show
```

## Testing Issues

### Test Failures

**Problem**: Testes falhando durante desenvolvimento

```bash
$ make test
FAILED tests/unit/test_domain.py::test_command_lifecycle
```

**Solutions**:

```bash
# Run specific test with verbose output
pytest tests/unit/test_domain.py::test_command_lifecycle -v -s

# Check test dependencies
poetry install --with test

# Clean test cache
pytest --cache-clear

# Run with debug output
pytest --pdb tests/unit/test_domain.py::test_command_lifecycle
```

### Coverage Issues

**Problem**: Cobertura de testes abaixo do mínimo (90%)

```bash
FAILED Required test coverage of 90% not reached. Total coverage: 85.23%
```

**Solutions**:

```bash
# Generate detailed coverage report
make coverage-html

# Open coverage report
open htmlcov/index.html

# Run coverage for specific module
pytest --cov=src/flext_cli/domain tests/unit/test_domain.py

# Exclude specific lines from coverage
# Add # pragma: no cover to lines that don't need coverage
```

### Slow Tests

**Problem**: Testes executando muito lentamente

```bash
$ make test
====== 45.67s elapsed ======
```

**Solutions**:

```bash
# Run only fast tests
pytest -m "not slow"

# Use parallel execution
pytest -n auto

# Skip integration tests during development
pytest -m unit

# Profile slow tests
pytest --durations=10
```

## Development Environment Issues

### IDE Configuration Problems

**Problem**: VS Code não reconhece tipos ou imports

```bash
"flext_cli" is not defined
```

**Solutions**:

1. **Configure Python Interpreter**:

   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Choose Poetry virtual environment

2. **Update VS Code settings**:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true
}
```

3. **Reload VS Code window**:
   - Ctrl+Shift+P → "Developer: Reload Window"

### Pre-commit Hook Failures

**Problem**: Pre-commit hooks falhando e bloqueando commits

```bash
$ git commit -m "Fix bug"
mypy....................................................................Failed
```

**Solutions**:

```bash
# Run pre-commit manually to see detailed errors
poetry run pre-commit run --all-files

# Fix specific issues
make lint           # Fix linting issues
make type-check     # Fix type issues
make format         # Fix formatting

# Skip hooks temporarily (emergency only)
git commit --no-verify -m "Emergency fix"

# Update pre-commit hooks
poetry run pre-commit autoupdate
```

## Performance Issues

### Slow CLI Response

**Problem**: CLI comandos executando lentamente

```bash
$ time poetry run flext config show
real    0m5.123s
```

**Solutions**:

```bash
# Use global installation instead of Poetry
make install-cli
flext config show

# Profile CLI startup
poetry run python -m cProfile -o profile.stats -m flext_cli.cli --help

# Check for import bottlenecks
poetry run python -X importtime -m flext_cli.cli --help

# Use lighter imports in CLI code
# Import modules only when needed, not at module level
```

### Memory Usage Issues

**Problem**: Alto uso de memória durante execução

```bash
$ poetry run flext debug info
MemoryError: Unable to allocate memory
```

**Solutions**:

```bash
# Monitor memory usage
poetry run python -m memory_profiler flext_cli/cli.py

# Use generators instead of lists for large datasets
# Implement lazy loading for heavy imports
# Clear unused objects explicitly

# Increase available memory
export PYTHONHASHSEED=0
ulimit -v unlimited
```

## Network and Connectivity Issues

### API Connection Failures

**Problem**: Falha ao conectar com serviços FLEXT

```bash
ConnectionError: HTTPSConnectionPool(host='api.flext.sh', port=443)
```

**Solutions**:

```bash
# Test connectivity
curl -v https://api.flext.sh/health

# Use debug mode to see detailed errors
poetry run flext --debug auth status

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Use different endpoint
export FLEXT_API_URL=http://localhost:8080
poetry run flext config show
```

### Certificate Issues

**Problem**: Problemas de certificado SSL

```bash
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions**:

```bash
# Update certificates
# macOS
/Applications/Python\ 3.13/Install\ Certificates.command

# Linux
sudo apt-get update && sudo apt-get install ca-certificates

# Disable SSL verification (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

## Quality Gate Failures

### Linting Failures

**Problem**: Ruff linting falhando

```bash
$ make lint
Found 15 errors
```

**Solutions**:

```bash
# Auto-fix most issues
make format
poetry run ruff check --fix src/ tests/

# Show specific errors
poetry run ruff check src/ tests/ --show-source

# Ignore specific rules temporarily
# Add # noqa: E501 to ignore line length
# Add # ruff: noqa to ignore entire file
```

### Type Checking Failures

**Problem**: MyPy type checking falhando

```bash
$ make type-check
src/flext_cli/cli.py:45: error: Incompatible return value type
```

**Solutions**:

```bash
# Show detailed error information
poetry run mypy src/ --show-error-codes --show-traceback

# Fix common type issues
# Add type hints: def func() -> None:
# Use Union types: Union[str, None] or str | None
# Use TYPE_CHECKING imports

# Generate type stubs for untyped libraries
poetry run stubgen -p untyped_package
```

### Security Scan Failures

**Problem**: Bandit security scan falhando

```bash
$ make security
Issue: [B602:subprocess_popen_with_shell_equals_true]
```

**Solutions**:

```bash
# Show detailed security issues
poetry run bandit -r src/ -f json

# Fix common security issues
# Use subprocess.run() with shell=False
# Validate user inputs
# Use secrets module for sensitive data

# Skip specific issues
# Add # nosec comment to ignore specific line
```

## Data and File Issues

### File Permission Problems

**Problem**: Problemas de permissão ao acessar arquivos

```bash
PermissionError: [Errno 13] Permission denied: '/path/to/file'
```

**Solutions**:

```bash
# Check file permissions
ls -la /path/to/file

# Fix permissions
chmod 644 /path/to/file        # Read/write for owner, read for others
chmod 755 /path/to/directory   # Execute permission for directories

# Run with appropriate user
sudo -u appropriate_user poetry run flext command
```

### Data Format Issues

**Problem**: Problemas com formatos de dados

```bash
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Solutions**:

```bash
# Validate JSON format
echo '{"key": "value"}' | jq .

# Use debug mode to see raw data
poetry run flext --debug --output json config show

# Handle empty responses
# Check API response status codes
# Implement proper error handling for data parsing
```

## Emergency Procedures

### Reset Everything

Se todos os outros métodos falharem:

```bash
# 1. Clean environment
rm -rf .venv
rm -rf .mypy_cache
rm -rf .pytest_cache
rm -rf .ruff_cache

# 2. Reinstall dependencies
poetry env remove python
poetry install --sync

# 3. Reset configuration
rm -rf ~/.flx

# 4. Verify installation
make check
```

### Rollback Changes

```bash
# Revert to last working commit
git stash
git reset --hard HEAD~1

# Reinstall dependencies
poetry install --sync

# Run tests
make test
```

## Getting Help

### Debug Information Collection

Ao reportar problemas, inclua as seguintes informações:

```bash
# System information
poetry run flext debug info

# Environment information
poetry env info
poetry show

# Error details with debug mode
poetry run flext --debug command 2>&1 | tee error.log

# Python and dependency versions
python --version
poetry --version
poetry show flext-core
```

### Log Collection

```bash
# Enable verbose logging
export FLEXT_CLI_LOG_LEVEL=debug

# Run command and capture logs
poetry run flext --debug command > output.log 2>&1

# System logs (if needed)
tail -f /var/log/syslog | grep python
```

### Community Support

1. **Check Documentation**:

   - [CLAUDE.md](../../CLAUDE.md)
   - [README.md](../../README.md)
   - [docs/](../)

2. **Search Issues**: Check existing GitHub issues

3. **Create Detailed Issue**: Include debug info, logs, and reproduction steps

---

**Next**: [Debugging Guide](debugging.md) | **Previous**: [Troubleshooting Home](../README.md)
