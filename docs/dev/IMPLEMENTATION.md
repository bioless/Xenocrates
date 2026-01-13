# Implementation Plan: Excel & JSON Input Format Support

**Status**: In Progress
**Branch**: `claude/add-excel-json-support-Ys0fs`
**Date Created**: 2026-01-12

---

## Overview

Add support for Excel (.xlsx) and JSON input formats to Xenocrates while maintaining full backward compatibility with existing TSV/CSV functionality.

---

## Problem Statement

Currently, Xenocrates only accepts TSV/CSV input files. However:
- Many GIAC students maintain their exam notes in **Excel spreadsheets** during courses
- Users who want to **programmatically generate** index files prefer **JSON** format
- Converting Excel → CSV → Xenocrates adds unnecessary friction

Adding native support for these formats will improve the user experience significantly.

---

## Goals

- ✅ Support Excel (.xlsx) files using `openpyxl` library
- ✅ Support JSON files using Python stdlib (no new dependencies)
- ✅ Auto-detect input format based on file extension
- ✅ Reuse existing column validation and normalization logic
- ✅ Maintain 100% backward compatibility with TSV/CSV files
- ✅ Keep error messages helpful and consistent across formats
- ✅ Preserve zero-dependency option for users who only need CSV/TSV

---

## Non-Goals (Future Considerations)

- ❌ Excel 97-2003 (.xls) legacy format support
- ❌ Google Sheets API integration
- ❌ Writing/exporting to Excel or JSON (read-only for now)
- ❌ Support for Excel files with multiple sheets (use first/active sheet only)
- ❌ SQLite database format

---

## Technical Design

### Architecture Changes

#### Current Flow
```
Input File (TSV/CSV)
    ↓
detect_delimiter() → csv.DictReader()
    ↓
validate_columns()
    ↓
read_index_data() → returns (index, has_course_column)
    ↓
generate_index() → HTML output
```

#### New Flow
```
Input File (TSV/CSV/XLSX/JSON)
    ↓
detect_file_format() → Dispatcher
    ↓
┌─────────────┬──────────────┬──────────────┐
│ CSV/TSV     │ Excel        │ JSON         │
│ (existing)  │ (new)        │ (new)        │
└─────────────┴──────────────┴──────────────┘
    ↓
validate_columns() [SHARED - reused across all formats]
    ↓
read_input_file() → returns (index, has_course_column)
    ↓
generate_index() → HTML output
```

### New Functions

#### 1. `detect_file_format(filename)` → str
```python
def detect_file_format(filename):
    """
    Detect input file format from extension.

    Args:
        filename: Path to input file

    Returns:
        str: Format identifier ('csv', 'tsv', 'excel', 'json')

    Raises:
        ValueError: If extension is not recognized
    """
```

**Logic:**
- `.xlsx` → `'excel'`
- `.csv` → `'csv'`
- `.tsv` → `'tsv'`
- `.json` → `'json'`
- `.txt` → `'csv'` (assume CSV, will auto-detect delimiter)
- Unknown → Raise helpful error with supported formats list

---

#### 2. `read_excel_data(filename)` → (list, bool)
```python
def read_excel_data(filename):
    """
    Read and parse Excel file (.xlsx) into index entries.

    Args:
        filename: Path to Excel file

    Returns:
        tuple: (index_data, has_course_column)
            - index_data: List of [title_upper, description, page, book, course]
            - has_course_column: Boolean indicating if Course column present

    Raises:
        ValueError: If required columns missing or validation fails
        ImportError: If openpyxl not installed
    """
```

**Implementation Notes:**
- Use `openpyxl.load_workbook(filename, read_only=True, data_only=True)`
  - `read_only=True`: Performance optimization for large files
  - `data_only=True`: Read calculated values, not formulas
- Read from first/active worksheet only
- First row = headers (case-insensitive matching)
- Subsequent rows = data
- **Reuse existing validation**: Pass headers to `validate_columns()`
- **Reuse existing parsing logic**: Same duplicate detection, empty title skipping, etc.
- Handle cells with `None` values (empty cells) → convert to empty string

**Error Handling:**
- If `openpyxl` not installed: Friendly error with `pip install openpyxl`
- Invalid Excel file: "Unable to read Excel file: [reason]"
- Missing required columns: Use existing column validation errors

---

#### 3. `read_json_data(filename)` → (list, bool)
```python
def read_json_data(filename):
    """
    Read and parse JSON file into index entries.

    Args:
        filename: Path to JSON file

    Returns:
        tuple: (index_data, has_course_column)
            - index_data: List of [title_upper, description, page, book, course]
            - has_course_column: Boolean indicating if Course column present

    Raises:
        ValueError: If JSON invalid, required fields missing, or validation fails
        json.JSONDecodeError: If file is not valid JSON
    """
```

**Supported JSON Structures:**

**Format 1: Wrapped (Recommended)**
```json
{
  "entries": [
    {
      "Title": "AES Encryption",
      "Description": "Advanced Encryption Standard symmetric cipher",
      "Page": "142",
      "Book": "SEC401",
      "Course": "SEC575"
    }
  ]
}
```

**Format 2: Direct Array**
```json
[
  {
    "Title": "AES Encryption",
    "Description": "Advanced Encryption Standard",
    "Page": "142",
    "Book": "SEC401"
  }
]
```

**Implementation Notes:**
- Accept both formats (check if root is dict or list)
- If dict, expect `"entries"` key containing array
- If array, use directly
- **Reuse existing validation**: Extract keys from first entry, validate columns
- Field names are case-insensitive (same as CSV/Excel)
- **Reuse existing parsing logic**: Same duplicate detection, empty title handling

**Error Handling:**
- Invalid JSON: "Invalid JSON format: [error]"
- Empty entries array: "JSON file contains no entries"
- Missing required fields: Use existing column validation errors

---

#### 4. `read_input_file(filename)` → (list, bool)
```python
def read_input_file(filename):
    """
    Read input file in any supported format (CSV/TSV/Excel/JSON).
    Unified entry point that dispatches to format-specific readers.

    Args:
        filename: Path to input file

    Returns:
        tuple: (index_data, has_course_column)
            - index_data: List of [title_upper, description, page, book, course]
            - has_course_column: Boolean indicating if Course column present

    Raises:
        ValueError: If format unsupported or file invalid
        FileNotFoundError: If file doesn't exist
    """
```

**Implementation:**
```python
def read_input_file(filename):
    file_format = detect_file_format(filename)

    readers = {
        'csv': read_csv_data,      # Rename from read_index_data
        'tsv': read_csv_data,      # Same handler
        'excel': read_excel_data,
        'json': read_json_data,
    }

    reader = readers[file_format]
    return reader(filename)
```

---

### Modified Functions

#### `read_index_data()` → Rename to `read_csv_data()`
- Keep all existing logic intact
- Just rename for consistency with new architecture
- Internal function, not breaking change (not public API)

#### `generate_index(input_file, output_file)`
- Change: Call `read_input_file()` instead of `read_index_data()`
- Everything else unchanged

---

## File Format Specifications

### Excel (.xlsx)

**Sheet Selection:**
- Use first worksheet (active sheet)
- Ignore other sheets if multiple exist

**Column Headers:**
- First row = headers
- Case-insensitive matching (same as CSV)
- Can be in any order

**Data Rows:**
- Row 2 onwards = data
- Empty cells treated as empty strings
- Leading/trailing whitespace stripped

**Required Columns:**
- Title
- Description
- Page
- Book

**Optional Columns:**
- Course (GSE mode)

**Example:**
```
| Title         | Description                  | Page | Book   | Course  |
|---------------|------------------------------|------|--------|---------|
| AES           | Symmetric encryption         | 142  | SEC401 | SEC575  |
| Kerberos      | Authentication protocol      | 201  | SEC505 |         |
```

---

### JSON

**Schema:**

```json
{
  "entries": [
    {
      "Title": "string (required)",
      "Description": "string (required)",
      "Page": "string (required)",
      "Book": "string (required)",
      "Course": "string (optional)"
    }
  ]
}
```

**Notes:**
- Field names case-insensitive (title = Title = TITLE)
- Field order doesn't matter
- `"entries"` wrapper is optional (can use direct array)
- Values are strings (even Page numbers)
- Empty/missing optional fields treated as empty string

**Example:**
```json
{
  "entries": [
    {
      "Title": "AES Encryption",
      "Description": "Advanced Encryption Standard symmetric cipher",
      "Page": "142",
      "Book": "SEC401",
      "Course": "SEC575"
    },
    {
      "Title": "Kerberos",
      "Description": "Network authentication protocol using tickets",
      "Page": "201",
      "Book": "SEC505"
    }
  ]
}
```

---

## Dependencies

### New Dependencies

**Add to `requirements.txt`:**
```
openpyxl==3.1.2
```

**Installation:**
```bash
pip install openpyxl
```

**Why openpyxl?**
- Industry standard for reading .xlsx files
- Actively maintained (last release: 2023)
- Read-only mode is performant
- ~2MB install size
- Pure Python (no C dependencies)
- Compatible with Python 3.8+

### Keeping Zero-Dependency Option

For users who only need CSV/TSV support, we should:
1. Make `openpyxl` optional (don't fail on import)
2. Show helpful error only when trying to read .xlsx without it
3. Document this in README

**Error message when openpyxl missing:**
```
Error: Excel file support requires openpyxl library.
Install with: pip install openpyxl

Alternatively, export your Excel file to CSV format.
```

---

## Testing Strategy

### Test Files to Create

#### 1. `tests/test-data-excel.xlsx`
- Excel version of existing `test-data-basic.tsv`
- 80+ entries covering A-Z sections
- Test alphabetical sorting
- Mix of books (SEC401, SEC504, etc.)

#### 2. `tests/test-data-excel-gse.xlsx`
- Excel version with Course column
- Test GSE mode detection
- Multiple courses per entry

#### 3. `tests/test-data.json`
- JSON version of basic test data
- Use wrapped format (`{"entries": [...]}`)
- Test standard 4-column format

#### 4. `tests/test-data-json-gse.json`
- JSON with Course column
- Test GSE mode in JSON

#### 5. `tests/test-data-json-direct.json`
- Direct array format (no "entries" wrapper)
- Verify both JSON formats work

#### 6. `tests/test-excel-lowercase-columns.xlsx`
- Column headers: "title", "description", "page", "book"
- Verify case-insensitive matching works

### Manual Testing Checklist

- [ ] Excel with standard columns works
- [ ] Excel with GSE columns (Course) works
- [ ] Excel with lowercase column names works
- [ ] JSON wrapped format works
- [ ] JSON direct array format works
- [ ] JSON with GSE columns works
- [ ] CSV/TSV files still work (backward compatibility)
- [ ] Auto-detection works for all formats
- [ ] Error handling for missing openpyxl
- [ ] Error handling for invalid Excel files
- [ ] Error handling for invalid JSON
- [ ] Error handling for missing required columns
- [ ] Special characters and HTML escaping work in all formats
- [ ] Duplicate detection works in all formats
- [ ] Empty title skipping works in all formats
- [ ] Large files (1000+ entries) work in all formats

### Regression Testing

**Must verify these existing test cases still pass:**
- `tests/test-data-basic.tsv` → Output unchanged
- `tests/test-data-csv.csv` → Output unchanged
- `tests/test-data-edge-cases.tsv` → HTML escaping works
- `tests/test-gse-with-course.tsv` → GSE mode works
- `tests/test-lowercase-columns.tsv` → Case-insensitive works

---

## Implementation Checklist

### Phase 1: Setup & Infrastructure
- [ ] Create this IMPLEMENTATION.md file
- [ ] Add `openpyxl==3.1.2` to requirements.txt
- [ ] Create requirements.txt if it doesn't exist
- [ ] Install openpyxl in development environment

### Phase 2: Core Implementation
- [ ] Implement `detect_file_format(filename)`
- [ ] Rename `read_index_data()` to `read_csv_data()`
- [ ] Implement `read_excel_data(filename)`
- [ ] Implement `read_json_data(filename)`
- [ ] Implement `read_input_file(filename)` dispatcher
- [ ] Update `generate_index()` to use `read_input_file()`

### Phase 3: Error Handling
- [ ] Add graceful handling for missing openpyxl
- [ ] Add helpful error messages for invalid Excel files
- [ ] Add helpful error messages for invalid JSON
- [ ] Ensure error messages consistent across formats
- [ ] Test unsupported file extensions show helpful error

### Phase 4: Testing
- [ ] Create `tests/test-data-excel.xlsx`
- [ ] Create `tests/test-data-excel-gse.xlsx`
- [ ] Create `tests/test-data.json`
- [ ] Create `tests/test-data-json-gse.json`
- [ ] Create `tests/test-data-json-direct.json`
- [ ] Create `tests/test-excel-lowercase-columns.xlsx`
- [ ] Test all new files generate correct output
- [ ] Verify all existing TSV/CSV tests still pass
- [ ] Test error cases (missing columns, invalid files)

### Phase 5: Documentation
- [ ] Update README.md with Excel format example
- [ ] Update README.md with JSON format example
- [ ] Update README.md with supported formats list
- [ ] Update CLI help text (`--help`)
- [ ] Add installation instructions for openpyxl
- [ ] Document JSON schema specification
- [ ] Add examples to documentation

### Phase 6: Polish & Review
- [ ] Self-review all code changes
- [ ] Check code style consistency
- [ ] Verify no breaking changes to existing functionality
- [ ] Test on sample user data if available
- [ ] Update IMPLEMENTATION.md with any deviations from plan

### Phase 7: Commit & Push
- [ ] Commit with clear message
- [ ] Push to `claude/add-excel-json-support-Ys0fs` branch
- [ ] Create pull request
- [ ] Mark IMPLEMENTATION.md as completed

---

## Breaking Changes

**None.** This is purely additive functionality.

- All existing CSV/TSV files will continue to work
- No changes to command-line interface
- No changes to output format
- No changes to existing function behavior

---

## Performance Considerations

### Excel Files
- Use `read_only=True` mode in openpyxl (faster, lower memory)
- For files with 10,000+ rows, may be slower than CSV
- Acceptable tradeoff for user convenience

### JSON Files
- Should be similar performance to CSV
- Python's `json` module is C-optimized
- May use slightly more memory for large files (entire file loaded at once)

### CSV/TSV Files (Existing)
- No performance impact
- Same implementation as before

---

## Future Enhancements (Post-Implementation)

These are explicitly out of scope for this PR but could be added later:

1. **Excel Legacy Format (.xls)**
   - Requires `xlrd` library
   - Add if users request it

2. **Google Sheets Integration**
   - Use `gspread` library
   - Requires OAuth setup
   - Significant complexity

3. **SQLite Database Support**
   - Use stdlib `sqlite3`
   - Good for very large datasets (10,000+ entries)

4. **Multiple Excel Sheets**
   - Currently use first/active sheet only
   - Could add `--sheet` CLI flag

5. **Excel Export**
   - Reverse operation: HTML → Excel
   - Requires `openpyxl` write mode

6. **JSON Schema Validation**
   - Add `jsonschema` validation
   - Better error messages for malformed JSON

---

## Success Criteria

### Must Have
- ✅ Can run: `xenocrates notes.xlsx output.html`
- ✅ Can run: `xenocrates notes.json output.html`
- ✅ Excel files with 100+ entries work correctly
- ✅ JSON files with 100+ entries work correctly
- ✅ All existing CSV/TSV tests pass unchanged
- ✅ Error messages remain helpful and actionable

### Nice to Have
- ✅ Performance acceptable for 1000+ entry files
- ✅ README has clear examples for all formats
- ✅ Installation instructions are beginner-friendly

---

## Questions & Decisions

### Q: Should we support Excel files without openpyxl installed?
**Decision:** No. Show helpful error message with installation instructions.

**Rationale:**
- Keeping the library optional adds complexity
- Users wanting Excel support will install one dependency
- Error message makes it clear what to do

### Q: Should JSON field names be case-sensitive?
**Decision:** No. Use same case-insensitive matching as CSV/Excel.

**Rationale:**
- Consistency across formats
- User-friendly (less chance of errors)
- Reuse existing `normalize_column_names()` logic

### Q: What if Excel file has multiple sheets?
**Decision:** Use first/active sheet only. Document this limitation.

**Rationale:**
- Simplest implementation
- Covers 95% of use cases
- Can add sheet selection later if needed

### Q: Should we validate JSON against a schema?
**Decision:** Not in initial implementation. Use same column validation as other formats.

**Rationale:**
- Reuse existing validation logic
- Don't introduce new dependencies (`jsonschema`)
- Error messages already good enough

---

## Notes & Observations

- Current codebase is very clean and well-structured
- Excellent error handling and user-friendly messages
- Column validation logic is reusable (great design!)
- No dependencies is a feature, not a limitation
- Adding openpyxl is acceptable tradeoff for Excel support

---

## References

- **openpyxl documentation:** https://openpyxl.readthedocs.io/
- **Python json module:** https://docs.python.org/3/library/json.html
- **Existing code:** `/home/user/Xenocrates/xenocrates.py`

---

**Last Updated:** 2026-01-12
**Status:** Ready for implementation
