# Testing Guide for Sentio 2.0

This guide explains how to test the Sentio 2.0 trading system.

## Prerequisites

### Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest sentio/tests/test_config.py

# Run specific test function
pytest sentio/tests/test_config.py::test_trading_mode_enum
```

### Test Coverage

```bash
# Run tests with coverage report
pytest --cov=sentio --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

### Test Markers

Tests are organized with markers for different categories:

```bash
# Run only unit tests (fast, no external dependencies)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Code Quality Validation

### Quick Validation

Run the built-in code quality validation script:

```bash
python validate_code.py
```

This checks for:
- Python syntax errors
- Wildcard imports
- Mutable default arguments
- TODO/FIXME comments

### Import Testing

Verify that all modules can be imported:

```bash
python test_import.py
```

## Testing Without Installing Dependencies

### Syntax Validation

Check that all Python files have valid syntax:

```bash
python -m compileall sentio/ -q
```

### Individual Module Testing

Test specific modules without full dependency installation:

```bash
# Test configuration module
python -c "from sentio.core.config import get_config; print('✅ Config module OK')"

# Test logger module (requires python-json-logger)
python -c "from sentio.core.logger import get_logger; print('✅ Logger module OK')"
```

## Writing Tests

### Test Structure

Follow this structure for new tests:

```python
"""
Tests for [module name]
"""
import pytest
from sentio.[module] import [classes/functions]


def test_[feature_name]():
    """Test [specific behavior]"""
    # Arrange
    input_data = ...
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected_value
```

### Fixtures

Use pytest fixtures for reusable test data:

```python
@pytest.fixture
def sample_market_data():
    """Create sample OHLCV data"""
    return pd.DataFrame({
        'open': [100, 101, 102],
        'high': [105, 106, 107],
        'low': [95, 96, 97],
        'close': [102, 103, 104],
        'volume': [1000000, 1100000, 1200000]
    })


def test_strategy_with_data(sample_market_data):
    """Test strategy using fixture"""
    strategy = MyStrategy()
    signal = strategy.execute(sample_market_data)
    assert signal.confidence > 0
```

## Continuous Testing

### Watch Mode

For development, you can use pytest-watch (install separately):

```bash
pip install pytest-watch
ptw  # Automatically runs tests when files change
```

### Pre-commit Checks

Before committing, run:

```bash
# Validate code quality
python validate_code.py

# Run all tests
pytest

# Check test coverage
pytest --cov=sentio --cov-report=term-missing
```

## Test Categories

### Unit Tests (`sentio/tests/test_*.py`)

- **test_config.py**: Configuration management tests
- **test_logger.py**: Logging system tests
- **test_base_strategy.py**: Base strategy class tests

### Integration Tests (Future)

Integration tests will test:
- API endpoints
- Database operations
- External service integrations
- End-to-end trading workflows

## Troubleshooting

### Import Errors

If you get import errors when running tests:

```bash
# Ensure package is installed in development mode
pip install -e .

# Or add current directory to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

For development dependencies:

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

## Best Practices

1. **Write tests before fixing bugs**: Create a failing test that reproduces the bug
2. **Test edge cases**: Don't just test happy paths
3. **Keep tests isolated**: Each test should be independent
4. **Use descriptive names**: Test names should explain what they test
5. **Mock external dependencies**: Don't rely on external services in unit tests
6. **Maintain high coverage**: Aim for >80% code coverage
7. **Run tests frequently**: Test early and often during development

## CI/CD Integration

Sentio 2.0 includes comprehensive GitHub Actions workflows for automated testing and code quality validation.

### Automated Workflows

Three main workflows run on every push and pull request:

#### 1. Code Quality Workflow (`.github/workflows/code-quality.yml`)

Runs linting and type checking:

```yaml
- Black formatter check (code style)
- Flake8 linting (PEP 8 compliance)
- Pylint analysis (code quality)
- MyPy type checking (static type analysis)
- Code quality validation script
```

#### 2. Tests Workflow (`.github/workflows/tests.yml`)

Runs test suite across multiple Python versions:

```yaml
- Python versions: 3.9, 3.10, 3.11
- Unit tests (fast, isolated)
- Integration tests (API, database)
- Code coverage reporting
- Codecov integration
```

#### 3. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

Complete pipeline with all checks:

```yaml
Jobs:
  1. Code Quality (flake8, pylint, mypy)
  2. Test Suite (pytest with coverage)
  3. Build Verification (package build)
```

### Triggering CI/CD

Workflows automatically run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via GitHub Actions UI

### Viewing Results

1. Go to your GitHub repository
2. Click on "Actions" tab
3. Select a workflow run to see results
4. View detailed logs for each job

### Configuration Files

Linting and type checking configurations:

- **`.flake8`** - Flake8 linting rules
- **`.pylintrc`** - Pylint configuration
- **`mypy.ini`** - MyPy type checking settings
- **`pytest.ini`** - Pytest test discovery and markers

### Local CI/CD Simulation

Run the same checks locally before pushing:

```bash
# Code quality checks
python validate_code.py
flake8 sentio/
pylint sentio/
mypy sentio/ --config-file mypy.ini

# Run tests
pytest sentio/tests/ -v --cov=sentio

# Build package
python -m build
```

### Pre-commit Integration

For automatic checks before commits, install pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (example)
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
EOF

# Install hooks
pre-commit install
```

### Example GitHub Actions workflow

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=sentio --cov-report=xml
    
- name: Validate code quality
  run: python validate_code.py
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
