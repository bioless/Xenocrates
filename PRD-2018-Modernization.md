# Product Requirements Document: Xenocrates 2018 Script Modernization

## Document Info
- **Version**: 1.0
- **Date**: 2026-01-12
- **Target File**: `xenocrates-update-2018.py`
- **Status**: Draft

---

## 1. Executive Summary

Modernize the `xenocrates-update-2018.py` script to ensure Python 3 compatibility, improve maintainability, and align with current best practices while preserving all existing functionality.

---

## 2. Background

### Current State
- Script written in 2018 using Python 2 syntax
- Processes tab-delimited files with columns: title, description, page, book, course
- Generates HTML output for GIAC certification exam indexing
- Contains deprecated Python 2 patterns and repetitive code

### Problem Statement
- Python 2 reached end-of-life in January 2020
- Script uses deprecated functions (`cgi.escape()`, file mode `'rU'`)
- Contains ~110 lines of repetitive if/elif logic
- Poor error handling (bare except clauses)
- Won't run on modern Python 3.11+ installations

---

## 3. Goals & Objectives

### Primary Goals
1. **Full Python 3 Compatibility**: Script must run on Python 3.8+
2. **Maintainability**: Reduce code complexity and improve readability
3. **Backward Compatibility**: Preserve exact HTML output format
4. **Reliability**: Improve error handling and user feedback

### Success Metrics
- Script runs without errors on Python 3.8, 3.10, 3.11, 3.12+
- Line count reduced by at least 50 lines
- Zero functional regressions (output matches original)
- Clear error messages for common failure scenarios

---

## 4. Functional Requirements

### Must Have (P0)
- **FR-1**: Accept tab-delimited input file as command-line argument
- **FR-2**: Parse CSV/TSV with columns: title, description, page, book, course
- **FR-3**: Alphabetically sort entries by title (case-insensitive)
- **FR-4**: Generate HTML output with alphabetical section headers (A-Z, 0-9)
- **FR-5**: HTML escape special characters in user data
- **FR-6**: Output to stdout for redirection
- **FR-7**: Handle entries starting with numbers (0-9 section)
- **FR-8**: Preserve exact HTML table structure and formatting

### Should Have (P1)
- **FR-9**: Validate input file exists before processing
- **FR-10**: Provide clear error messages for malformed data
- **FR-11**: Handle edge cases (empty files, missing columns)
- **FR-12**: Support both tab and comma delimiters

### Nice to Have (P2)
- **FR-13**: Add `--help` option for usage information
- **FR-14**: Support output to file via `--output` flag
- **FR-15**: Add `--version` flag

---

## 5. Technical Requirements

### Code Quality
- **TR-1**: Replace Python 2 print statements with Python 3 syntax
- **TR-2**: Replace `cgi.escape()` with `html.escape()`
- **TR-3**: Replace deprecated file mode `'rU'` with `'r'`
- **TR-4**: Use `#!/usr/bin/env python3` shebang
- **TR-5**: Eliminate repetitive if/elif chain (lines 36-144)
- **TR-6**: Replace bare `except:` with specific exception handling
- **TR-7**: Remove unused imports (sqlite3)
- **TR-8**: Remove unused variables (tablename)

### Modern Python Practices
- **TR-9**: Use f-strings instead of % formatting (where appropriate)
- **TR-10**: Use `string.ascii_uppercase` for alphabet iteration
- **TR-11**: Use context managers (`with` statements) for file I/O
- **TR-12**: Add type hints (optional, nice-to-have)
- **TR-13**: Follow PEP 8 style guidelines

### Error Handling
- **TR-14**: Validate command-line arguments
- **TR-15**: Handle FileNotFoundError with clear message
- **TR-16**: Handle CSV parsing errors gracefully
- **TR-17**: Exit with appropriate status codes (0=success, 1=error)

---

## 6. Non-Functional Requirements

### Compatibility
- **NFR-1**: Minimum Python version: 3.8
- **NFR-2**: No external dependencies beyond Python stdlib
- **NFR-3**: Cross-platform (Linux, macOS, Windows)

### Performance
- **NFR-4**: Process files up to 10,000 rows in under 5 seconds
- **NFR-5**: Memory usage proportional to file size

### Maintainability
- **NFR-6**: Code should be self-documenting with clear variable names
- **NFR-7**: Complex logic should include inline comments
- **NFR-8**: Main processing logic under 200 lines

---

## 7. Implementation Plan

### Phase 1: Critical Updates (P0)
1. Update Python 2 → 3 syntax
2. Replace deprecated functions
3. Refactor if/elif chain
4. Basic error handling

### Phase 2: Quality Improvements (P1)
1. Improve error messages
2. Add input validation
3. Code cleanup and optimization

### Phase 3: Enhanced Features (P2)
1. Add command-line flags
2. Enhanced output options
3. Documentation

---

## 8. Testing Requirements

### Test Cases
- **TC-1**: Process sample file with all alphabetic sections
- **TC-2**: Process file with numeric entries (0-9)
- **TC-3**: Handle special characters in title/description
- **TC-4**: Process empty file
- **TC-5**: Handle missing columns gracefully
- **TC-6**: Verify HTML output matches original script output
- **TC-7**: Test on Python 3.8, 3.10, 3.11, 3.12

### Regression Testing
- Compare HTML output byte-for-byte with original script
- Verify alphabetical sorting is preserved
- Ensure HTML table structure is unchanged

---

## 9. Out of Scope

The following are explicitly **NOT** included in this update:
- ❌ Changing HTML output format or styling
- ❌ Adding web framework or server functionality
- ❌ Database integration
- ❌ GUI interface
- ❌ Support for non-TSV/CSV input formats (Excel, JSON, etc.)
- ❌ Internationalization (i18n) support
- ❌ Changes to xenocrates.py or xenocrates-gse.py (separate scope)

---

## 10. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking backward compatibility | High | Medium | Comprehensive regression testing |
| Different HTML output | High | Low | Byte-level comparison tests |
| Sorting behavior changes | Medium | Low | Unit tests for sorting logic |
| Python 3.8+ unavailable | Low | Low | Document minimum version clearly |

---

## 11. Dependencies

- None (Python stdlib only)

---

## 12. Acceptance Criteria

The modernization is complete when:
- ✅ All P0 functional requirements are met
- ✅ All P0 technical requirements are implemented
- ✅ Script runs on Python 3.8+
- ✅ All test cases pass
- ✅ HTML output matches original (for same input)
- ✅ Code review completed
- ✅ Documentation updated

---

## 13. Open Questions

1. Should we maintain Python 2 compatibility or fully commit to Python 3?
   - **Decision**: Python 3 only (Python 2 is EOL since 2020)

2. Should we rename the file to remove "2018" designation?
   - **Decision**: TBD - discuss with stakeholders

3. What Python versions should we test against?
   - **Decision**: 3.8 (oldest supported), 3.11, 3.12 (latest)

---

## Appendix A: Current Code Issues

### Deprecated Patterns
```python
# Line 1
#!/usr/bin/python  # Should be python3

# Line 18
with open(sys.argv[1], 'rU') as tsvin:  # 'rU' deprecated in 3.11

# Line 23
cgi.escape(str(row['title']))  # cgi.escape deprecated, use html.escape

# Line 38-151
# 114 lines of repetitive if/elif for A-Z
```

### Code Smells
- Lines 36-144: Massive duplication (DRY violation)
- Line 24: Bare except clause
- Line 12: Unused variable `tablename`
- Line 2: Unused import `sqlite3`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-12 | Initial | Initial PRD creation |

