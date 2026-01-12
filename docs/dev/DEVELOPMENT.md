# Xenocrates Development Guide

This document explains the development workflow, testing, and code quality tools for Xenocrates.

## Quick Start for Developers

```bash
# 1. Clone and setup
git clone https://github.com/bioless/Xenocrates.git
cd Xenocrates

# 2. Install dependencies
make install-dev

# 3. Run tests
make test

# 4. Check code quality
make check

# 5. Make changes, then format and test
make format
make test
make lint
```

---

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage report
make test-coverage

# Run tests directly with pytest
pytest tests/ -v
```

### Test Organization

Tests are located in `tests/test_xenocrates.py` and organized into classes:

- **TestFileFormatDetection** - File format detection from extensions
- **TestColumnValidation** - Column validation and normalization
- **TestCSVReading** - CSV/TSV file parsing
- **TestExcelReading** - Excel file parsing
- **TestJSONReading** - JSON file parsing
- **TestUnifiedReader** - Format dispatcher
- **TestDataQuality** - Data quality features
- **TestErrorHandling** - Error conditions
- **TestSectionHeaders** - Section header generation
- **TestIntegration** - End-to-end pipelines

**Test Coverage:** 41 tests covering all major functionality

### Writing New Tests

```python
# Add tests to tests/test_xenocrates.py

class TestMyNewFeature:
    """Test description."""

    def test_something(self):
        """Test a specific behavior."""
        result = xenocrates.my_function()
        assert result == expected_value
```

---

## Code Quality

### Code Formatting

```bash
# Auto-format code with black and isort
make format

# Check formatting without making changes
make format-check

# Format specific files
black xenocrates.py
isort xenocrates.py
```

**Configuration:** See `pyproject.toml` for black and isort settings

### Linting

```bash
# Run flake8 linter
make lint

# Run directly
flake8 xenocrates.py tests/
```

**Configuration:** See `.flake8` for linting rules

### Running All Checks

```bash
# Run linting + format checking
make check
```

---

## Makefile Commands

The `Makefile` provides convenient development commands:

### Setup
- `make install` - Install production dependencies
- `make install-dev` - Install development + production dependencies

### Testing
- `make test` - Run all tests
- `make test-verbose` - Run tests with detailed output
- `make test-coverage` - Run tests with coverage report

### Code Quality
- `make lint` - Check code with flake8
- `make format` - Format code with black and isort
- `make check` - Run all quality checks (lint + format check)

### Utilities
- `make clean` - Remove temporary files and caches
- `make versions` - Show versions of all tools
- `make help` - Show all available commands

---

## Dependencies

### Production Dependencies (`requirements.txt`)
```
openpyxl==3.1.2  # Excel file support
```

### Development Dependencies (`requirements-dev.txt`)
```
pytest>=7.4.0           # Testing framework
pytest-cov>=4.1.0       # Coverage reports
black>=23.0.0           # Code formatter
flake8>=6.0.0           # Style checker
isort>=5.12.0           # Import sorter
```

### Installing Dependencies

```bash
# Production only (for end users)
pip install -r requirements.txt

# Development (for contributors)
pip install -r requirements-dev.txt
```

---

## Workflow for Contributors

### 1. Before Making Changes

```bash
# Create feature branch
git checkout -b feature/my-feature

# Install dev dependencies
make install-dev

# Run tests to ensure everything works
make test
```

### 2. While Making Changes

```bash
# Edit code
vim xenocrates.py

# Format code
make format

# Run tests
make test

# Check linting
make lint
```

### 3. Before Committing

```bash
# Run all quality checks
make check

# Run tests
make test

# Stage changes
git add -A

# Commit with descriptive message
git commit -m "Add feature X"
```

### 4. Before Pushing

```bash
# Final check
make test
make check

# Push changes
git push origin feature/my-feature
```

---

## Configuration Files

### `pyproject.toml`
Configures black, isort, and pytest:
```toml
[tool.black]
line-length = 120

[tool.isort]
profile = "black"
line_length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### `.flake8`
Configures flake8 linter:
```ini
[flake8]
max-line-length = 120
exclude = .git, __pycache__, venv
```

### `Makefile`
Provides convenient development commands (see above)

---

## Testing Philosophy

### Why We Separate Tests from Main Code

✅ **Correct:**
```
xenocrates/
├── xenocrates.py          # Production code
├── tests/
│   └── test_xenocrates.py # Test code (separate!)
```

❌ **Wrong:**
```python
# DON'T put tests in main script
if __name__ == "__main__":
    assert my_function() == expected  # BAD!
```

**Benefits of Separation:**
1. Clean separation of concerns
2. No test code in production
3. Easier to maintain
4. Better organization
5. Industry standard

### Test Coverage Goals

- All public functions should have tests
- Error conditions should be tested
- Edge cases should be tested
- Integration tests for complete workflows

---

## Common Development Tasks

### Adding a New Input Format

1. **Write tests first** (TDD approach):
   ```python
   # tests/test_xenocrates.py
   def test_read_my_format(self):
       index, has_course = xenocrates.read_my_format('test.myformat')
       assert len(index) > 0
   ```

2. **Implement the reader**:
   ```python
   # xenocrates.py
   def read_my_format(filename):
       # ... implementation ...
       return index, has_course_column
   ```

3. **Add to format map**:
   ```python
   format_map = {
       '.xlsx': 'excel',
       '.json': 'json',
       '.myformat': 'myformat',  # Add new format
   }
   ```

4. **Add to dispatcher**:
   ```python
   readers = {
       'csv': read_csv_data,
       'excel': read_excel_data,
       'json': read_json_data,
       'myformat': read_my_format,  # Add new reader
   }
   ```

5. **Update documentation**:
   - Update README.md
   - Update CHANGELOG.md
   - Update docstrings

6. **Test thoroughly**:
   ```bash
   make test
   make check
   ```

### Fixing a Bug

1. **Write a failing test** that reproduces the bug
2. **Fix the bug** in the code
3. **Verify the test now passes**
4. **Run all tests** to ensure no regressions
5. **Update CHANGELOG.md**

### Refactoring Code

1. **Run tests before refactoring** (should pass)
2. **Refactor the code**
3. **Run tests after refactoring** (should still pass)
4. **Run linting**: `make check`
5. **Format code**: `make format`

---

## Troubleshooting

### Tests Fail After Changes

```bash
# Run with verbose output to see details
pytest tests/test_xenocrates.py -vv

# Run a specific test
pytest tests/test_xenocrates.py::TestCSVReading::test_read_basic_tsv -v
```

### Linting Errors

```bash
# See what's wrong
make lint

# Auto-fix formatting issues
make format

# Check again
make lint
```

### Import Errors in Tests

Make sure you're running from the project root:
```bash
cd /path/to/Xenocrates
python3 -m pytest tests/
```

---

## Best Practices

### Code Style
1. Follow PEP 8 (enforced by flake8)
2. Use black for formatting (automatic)
3. Keep lines under 120 characters
4. Write descriptive variable names
5. Add docstrings to functions

### Testing
1. Write tests for new features
2. Test error conditions
3. Test edge cases
4. Keep tests independent
5. Use descriptive test names

### Git Commits
1. Write clear commit messages
2. Keep commits focused
3. Reference issues when applicable
4. Update CHANGELOG.md
5. Run tests before committing

### Documentation
1. Update README.md for user-facing changes
2. Update CHANGELOG.md for all changes
3. Write clear docstrings
4. Add code comments for complex logic
5. Keep DEVELOPMENT.md up to date

---

## Resources

- **pytest documentation:** https://docs.pytest.org/
- **black documentation:** https://black.readthedocs.io/
- **flake8 documentation:** https://flake8.pycqa.org/
- **isort documentation:** https://pycqa.github.io/isort/
- **Keep a Changelog:** https://keepachangelog.com/

---

## Getting Help

If you encounter issues:

1. Check this DEVELOPMENT.md guide
2. Run `make help` to see available commands
3. Check test output: `make test-verbose`
4. Check linting: `make lint`
5. Open an issue on GitHub

---

**Last Updated:** 2026-01-12
**Maintained By:** Xenocrates contributors
