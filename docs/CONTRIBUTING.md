# Contributing to Sentio 2.0

Thank you for your interest in contributing to Sentio 2.0! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the best solution for the project
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Relevant logs or error messages

### Suggesting Enhancements

1. Check if the feature has been requested
2. Create an issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternatives you've considered
   - Potential impact on existing features

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Write or update tests as needed
5. Ensure all tests pass
6. Update documentation
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Sentio-2.0.git
cd Sentio-2.0

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest
```

## Coding Standards

### Python Style
- Follow PEP 8
- Use type hints
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Use meaningful variable names

### Example:
```python
def calculate_position_size(
    portfolio_value: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss: float
) -> float:
    """
    Calculate optimal position size using risk-based sizing.
    
    Args:
        portfolio_value: Current portfolio value
        risk_per_trade: Risk percentage per trade (e.g., 0.02 for 2%)
        entry_price: Entry price
        stop_loss: Stop-loss price
        
    Returns:
        Position size (number of shares/contracts)
    """
    risk_amount = portfolio_value * risk_per_trade
    risk_per_share = abs(entry_price - stop_loss)
    
    if risk_per_share == 0:
        return 0
    
    return risk_amount / risk_per_share
```

### Testing
- Write tests for new features
- Maintain or improve code coverage (aim for 70%+ overall, 90%+ for critical modules)
- Test edge cases and error conditions
- Use meaningful test names that describe what's being tested
- Follow the testing guidelines in [TESTING.md](TESTING.md)

**Test Requirements**:
- All new features must include unit tests
- API changes must include integration tests
- Critical bug fixes must include regression tests
- Tests must pass before submitting PR

**Example Test Structure**:
```python
import pytest
from sentio.strategies.base import TradingSignal, SignalType

@pytest.mark.unit
class TestPositionSizing:
    
    @pytest.fixture
    def risk_manager(self):
        """Create risk manager instance"""
        return RiskManager()
    
    def test_position_size_calculation_with_valid_inputs(self, risk_manager):
        """Test position sizing with normal market conditions"""
        size = risk_manager.calculate_position_size(
            portfolio_value=100000,
            risk_per_trade=0.02,
            entry_price=100,
            stop_loss=98
        )
        # Risk: $2,000 / $2 per share = 1,000 shares
        # But limited by max_position_size constraint
        assert size == 50.0
    
    def test_position_size_with_zero_risk(self, risk_manager):
        """Test edge case: zero risk distance"""
        size = risk_manager.calculate_position_size(
            portfolio_value=100000,
            risk_per_trade=0.02,
            entry_price=100,
            stop_loss=100  # Same as entry
        )
        assert size == 0
```

**Running Tests**:
```bash
# All tests
pytest

# With coverage
pytest --cov=sentio --cov-report=html

# Specific tests
pytest sentio/tests/test_risk_manager.py

# By marker
pytest -m unit
```

For complete testing documentation, see [TESTING.md](TESTING.md).

### Documentation
- Update README.md for user-facing changes
- Update ARCHITECTURE.md for structural changes
- Add docstrings to all public APIs
- Include usage examples

### Commit Messages
Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

Example:
```
feat: add support for multi-timeframe analysis

- Implement timeframe aggregation
- Add tests for different timeframes
- Update documentation
```

## Adding New Features

### New Strategy
1. Create file in `sentio/strategies/`
2. Inherit from `BaseStrategy`
3. Implement required methods
4. Add tests
5. Update documentation

### New Indicator
1. Add to `sentio/analysis/technical_analysis.py`
2. Implement calculation method
3. Add to analysis pipeline
4. Write tests
5. Document usage

### New API Endpoint
1. Add to `sentio/ui/api.py`
2. Define request/response models
3. Implement endpoint logic
4. Add authentication/authorization
5. Write integration tests
6. Update API documentation

## Testing Guidelines

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=sentio --cov-report=html

# Specific file
pytest sentio/tests/test_strategies.py

# Specific test
pytest sentio/tests/test_strategies.py::test_tjr_strategy
```

### Test Structure
```python
import pytest
from sentio.strategies.tjr_strategy import TJRStrategy

class TestTJRStrategy:
    @pytest.fixture
    def strategy(self):
        return TJRStrategy()
    
    @pytest.fixture
    def sample_data(self):
        # Return sample OHLCV data
        pass
    
    def test_signal_generation(self, strategy, sample_data):
        signal = strategy.execute(sample_data)
        assert signal.confidence >= 0.0
        assert signal.confidence <= 1.0
```

## Review Process

### What We Look For
- Code quality and readability
- Test coverage
- Documentation completeness
- Performance considerations
- Security implications
- Backward compatibility

### Review Timeline
- Initial review within 3-5 days
- Follow-up reviews within 2 days
- Approval requires 1-2 maintainer reviews

## Getting Help

- GitHub Issues: For bugs and features
- Discussions: For questions and ideas
- Documentation: Check README and ARCHITECTURE.md first

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in commit messages (Co-authored-by)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Sentio 2.0!
