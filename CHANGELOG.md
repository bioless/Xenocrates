# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive automated test suite with pytest
- Code linting setup (black, flake8, isort)
- This CHANGELOG.md file

## [2.0.0] - 2026-01-12

### Added
- **Excel (.xlsx) input format support** - Use Excel files directly without exporting
- **JSON input format support** - Both wrapped (`{"entries": [...]}`) and direct array formats
- **Automatic format detection** - Detects format based on file extension
- **Unified reader architecture** - Single `read_input_file()` dispatcher for all formats
- **requirements.txt** - Dependencies file with openpyxl
- **IMPLEMENTATION.md** - Detailed design and implementation documentation
- **Comprehensive test files** for all formats:
  - `test-data-excel.xlsx` - Standard Excel format
  - `test-data-excel-gse.xlsx` - GSE format with Course column
  - `test-excel-lowercase-columns.xlsx` - Case-insensitive column test
  - `test-data.json` - JSON wrapped format
  - `test-data-json-direct.json` - JSON direct array format
  - `test-data-json-gse.json` - JSON GSE format
- **Test file generation script** - `create_test_files.py` for creating test data

### Changed
- Updated `README.md` with examples for Excel and JSON formats
- Enhanced CLI help text to show all supported formats
- Improved module docstring to document all input formats
- Refactored `read_index_data()` to `read_csv_data()` for naming consistency

### Fixed
- N/A (This release adds new features, no bugs fixed)

### Deprecated
- N/A

### Removed
- N/A

### Security
- Excel file parsing uses read-only mode for safety and performance
- All file formats properly handle special characters and HTML escaping

### Breaking Changes
None - This release is 100% backward compatible with version 1.x

## [1.0.0] - 2024-XX-XX

### Added
- **Python 3.8+ support** - Modernized from Python 2
- **GSE Support** - Optional Course column for multi-course indexes
- **Case-insensitive column names** - 'title' = 'Title' = 'TITLE'
- **Flexible column order** - Columns can be in any order (name-based, not position-based)
- **Smart error messages** - Typo suggestions using similarity scoring (e.g., 'Titel' → 'Title')
- **CSV/TSV auto-detection** - Automatically detects comma vs. tab delimiter
- **Direct file output** - Modern usage: `xenocrates.py input.tsv output.html`
- **Duplicate detection** - Warns about duplicate entries with row numbers
- **HTML escaping** - Proper handling of special characters using `html.escape()`
- **Help and version flags** - `--help` and `--version` command-line options
- **Cross-platform support** - Works on Mac, Windows, and Linux
- **Empty title handling** - Skips entries with empty titles and reports count
- **Column validation** - Validates required columns with helpful error messages
- **Alphabetical sorting** - Case-insensitive A-Z section organization

### Changed
- Migrated from Python 2 to Python 3
- Replaced `cgi.escape()` with `html.escape()` (Python 3 standard)
- Improved from position-based to name-based column access
- Changed from bare `except:` to specific exception handling
- Enhanced error messages with actionable suggestions

### Fixed
- Fixed quote escaping (old version didn't escape quotes properly)
- Fixed case-sensitivity issues in column matching
- Fixed error handling that was swallowing errors silently

### Deprecated
- Python 2 support (use archived versions for Python 2)
- Position-based column ordering (now name-based)

### Removed
- Python 2 compatibility code
- Legacy `cgi` module usage

### Security
- Improved HTML escaping to prevent XSS vulnerabilities
- Safer file handling with explicit encoding (UTF-8)
- Better error messages that don't expose system internals

## [0.x] - Legacy Python 2 Versions

Legacy versions are archived in the `archive/` directory:
- `archive/xenocrates.py` - Original Python 2 version
- `archive/xenocrates-gse.py` - GSE-specific variant
- `archive/xenocrates-update-2018.py` - 2018 update

These versions are no longer maintained but kept for reference.

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version (X.0.0) - Incompatible API changes
- **MINOR** version (1.X.0) - New functionality, backward compatible
- **PATCH** version (1.0.X) - Bug fixes, backward compatible

---

## Contributing

When contributing, please:
1. Update this CHANGELOG.md in the `[Unreleased]` section
2. Follow the format: Added, Changed, Fixed, Deprecated, Removed, Security
3. Move changes from `[Unreleased]` to a version section when releasing
4. Include issue/PR numbers where applicable

Example:
```markdown
### Added
- New feature description (#123)

### Fixed
- Bug fix description (#124)
```
