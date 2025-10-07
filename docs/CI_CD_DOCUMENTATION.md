# CI/CD Pipeline Documentation

## Overview

Sentio 2.0 uses GitHub Actions for continuous integration and continuous deployment (CI/CD). The pipeline automatically validates code quality, runs tests, and builds the package on every commit and pull request.

## Workflows

### 1. Code Quality Checks (`code-quality.yml`)

**Purpose**: Ensure code adheres to quality standards

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Steps**:
1. **Black Formatter Check** - Validates code formatting
   ```bash
   black --check --diff sentio/
   ```

2. **Flake8 Linting** - Checks PEP 8 compliance
   ```bash
   flake8 sentio/ --exit-zero --statistics
   ```

3. **Pylint Analysis** - Comprehensive code quality analysis
   ```bash
   pylint sentio/ --exit-zero --score=yes
   ```

4. **MyPy Type Checking** - Static type analysis
   ```bash
   mypy sentio/ --config-file mypy.ini --exit-zero
   ```

5. **Code Quality Validation** - Custom validation script
   ```bash
   python validate_code.py
   ```

### 2. Test Suite (`tests.yml`)

**Purpose**: Run comprehensive test suite across Python versions

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Matrix Strategy**:
- Python versions: 3.9, 3.10, 3.11
- OS: Ubuntu latest

**Steps**:
1. **Install Dependencies** - Install all required packages
2. **Run Unit Tests** - Fast, isolated tests
   ```bash
   pytest sentio/tests/ -m "unit" -v --tb=short
   ```

3. **Run Integration Tests** - API and database tests
   ```bash
   pytest sentio/tests/ -m "integration" -v --tb=short
   ```

4. **Coverage Report** - Generate code coverage
   ```bash
   pytest sentio/tests/ -v --cov=sentio --cov-report=xml --cov-report=term-missing
   ```

5. **Upload to Codecov** - Share coverage metrics
   - Only runs for Python 3.11
   - Uploads coverage.xml to Codecov

### 3. Complete CI/CD Pipeline (`ci-cd.yml`)

**Purpose**: Full pipeline with all validation steps

**Jobs**:

#### Job 1: Code Quality
- Runs all linting and type checking tools
- Validates code standards
- Must pass for subsequent jobs to run

#### Job 2: Test Suite
- Depends on: Code Quality job
- Runs on Python 3.9, 3.10, 3.11
- Executes all tests with coverage
- Uploads coverage reports

#### Job 3: Build Verification
- Depends on: Test Suite job
- Builds Python package
- Verifies installation
- Validates package structure

## Configuration Files

### Linting Configuration

**`.flake8`** - Flake8 settings
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,.pytest_cache,build,dist,venv
ignore = E203,W503,E501
max-complexity = 15
```

**`.pylintrc`** - Pylint settings
```ini
[MASTER]
jobs=0
persistent=yes

[MESSAGES CONTROL]
disable=C0103,C0114,C0115,C0116,R0801,R0902,R0903
```

**`mypy.ini`** - MyPy settings
```ini
[mypy]
python_version = 3.9
check_untyped_defs = True
warn_redundant_casts = True
warn_unused_ignores = True
```

### Test Configuration

**`pytest.ini`** - Pytest settings
```ini
[pytest]
testpaths = sentio/tests
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

## Running Locally

### Prerequisites

```bash
# Install development dependencies
pip install pytest pytest-cov pytest-asyncio httpx
pip install flake8 pylint mypy black
```

### Run All Checks

```bash
# 1. Code quality validation
python validate_code.py

# 2. Linting
flake8 sentio/
pylint sentio/

# 3. Type checking
mypy sentio/ --config-file mypy.ini

# 4. Tests with coverage
pytest sentio/tests/ -v --cov=sentio --cov-report=term-missing

# 5. Build package
python -m build
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest sentio/tests/ -m "unit" -v

# Integration tests only
pytest sentio/tests/ -m "integration" -v

# Specific test file
pytest sentio/tests/test_api.py -v

# Specific test function
pytest sentio/tests/test_api.py::TestAPIEndpoints::test_health_check_endpoint -v
```

## Code Coverage

### Current Coverage

The test suite provides coverage for:
- Core configuration module
- Base strategy implementation
- Logger functionality
- API endpoints
- Authentication and authorization
- Risk management
- Subscription management
- Trading engine
- Order execution

### Coverage Goals

- **Target**: 80%+ code coverage
- **Critical paths**: 90%+ coverage
- **New code**: Must have tests

### Viewing Coverage

```bash
# Terminal report
pytest --cov=sentio --cov-report=term-missing

# HTML report
pytest --cov=sentio --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=sentio --cov-report=xml
```

## Best Practices

### Before Committing

1. Run code quality validation:
   ```bash
   python validate_code.py
   ```

2. Run relevant tests:
   ```bash
   pytest sentio/tests/ -v
   ```

3. Check coverage for new code:
   ```bash
   pytest --cov=sentio --cov-report=term-missing
   ```

4. Format code:
   ```bash
   black sentio/
   ```

### Writing Tests

1. **Use appropriate markers**:
   ```python
   @pytest.mark.unit
   def test_function():
       pass
   
   @pytest.mark.integration
   def test_api_endpoint():
       pass
   ```

2. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test functions: `test_*`

3. **Use fixtures for reusable data**:
   ```python
   @pytest.fixture
   def sample_data():
       return {"key": "value"}
   ```

4. **Write descriptive test docstrings**:
   ```python
   def test_feature():
       """Test that feature X works correctly when Y"""
       pass
   ```

### Pull Request Checklist

- [ ] All tests pass locally
- [ ] Code coverage maintained or improved
- [ ] Linting passes (flake8, pylint)
- [ ] Type checking passes (mypy)
- [ ] Code formatted with Black
- [ ] New tests added for new features
- [ ] Documentation updated if needed

## Troubleshooting

### Common Issues

**Tests failing in CI but passing locally**
- Check Python version compatibility
- Ensure all dependencies are in requirements.txt
- Verify test isolation (no local state dependencies)

**Linting failures**
- Run `black sentio/` to auto-format
- Check `.flake8` for ignored rules
- Review pylint messages for code improvements

**Coverage drops**
- Add tests for new code
- Remove dead/unreachable code
- Check for untested edge cases

**Build failures**
- Verify setup.py configuration
- Check for missing dependencies
- Ensure all imports work

## Continuous Improvement

### Monitoring

- Review GitHub Actions logs regularly
- Monitor code coverage trends
- Track test execution time
- Identify flaky tests

### Optimization

- Cache pip dependencies
- Parallelize test execution
- Optimize slow tests
- Remove redundant checks

### Future Enhancements

- [ ] Add security scanning (Bandit)
- [ ] Add dependency vulnerability scanning
- [ ] Add performance benchmarking
- [ ] Add deployment automation
- [ ] Add automated changelog generation

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pylint Documentation](https://pylint.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
