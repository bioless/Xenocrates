# Xenocrates Test Data

This directory contains test data files for validating the Xenocrates index generation tool.

## Test Files

### 1. `test-data-minimal.tsv`
**Purpose**: Quick smoke testing
**Entries**: 6 entries (A, B, C, Z, numbers, symbols)
**Use case**: Fast validation that basic functionality works

**Usage**:
```bash
python xenocrates.py test-data-minimal.tsv > output-minimal.html
```

---

### 2. `test-data-basic.tsv`
**Purpose**: Comprehensive functional testing
**Entries**: 70+ entries covering all alphabet sections (A-Z) and numbers
**Content**: Realistic GIAC certification study topics including:
- Security concepts (encryption, firewalls, authentication)
- Forensics tools (Volatility, Wireshark, memory analysis)
- Network protocols (DNS, TCP, SSL/TLS)
- Attack techniques (XSS, SQL injection, malware)

**Coverage**:
- ✅ All 26 alphabetic sections (Aa - Zz)
- ✅ Numbers & Special Characters section
- ✅ Realistic security/forensics terminology
- ✅ Proper alphabetical sorting
- ✅ Mixed case handling

**Usage**:
```bash
python xenocrates.py test-data-basic.tsv > output-basic.html
```

---

### 3. `test-data-edge-cases.tsv`
**Purpose**: Edge case and error handling validation
**Entries**: 17 edge cases

**Test Scenarios**:
1. **HTML Injection**: `<script>alert(1)</script>` - ensures HTML escaping works
2. **Special Characters**:
   - Quotes: `"Quoted Title"`
   - Apostrophes: `O'Reilly Books`
   - Ampersands: `Command & Control`
   - Less-than/Greater-than: `5 < 10 < 20`, `a > b`
3. **Code Snippets**: SQL queries, bash shebangs
4. **HTML Entities**: `&nbsp;`, `<tag>`
5. **Empty Values**: Empty title field
6. **Duplicates**: Same title/page/book repeated
7. **Case Variations**: MiXeD CaSe, ALLCAPS, lowercase

**Expected Behavior**:
- HTML special characters should be properly escaped
- Titles with quotes/apostrophes handled correctly
- Empty titles should be skipped (current behavior)
- Duplicates should both appear (no deduplication)
- Case-insensitive sorting should group similar titles

**Usage**:
```bash
python xenocrates.py test-data-edge-cases.tsv > output-edge-cases.html
```

---

## File Format

All test files use **tab-delimited** format (TSV) with the following columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| Title | The term/topic being indexed | Yes | `AES Encryption` |
| Book | Course/book identifier | Yes | `SEC401` |
| Page | Page number reference | Yes | `142` |
| Description | Detailed explanation | No | `Advanced Encryption Standard...` |

**Important Notes**:
- First row must be the header: `Title	Book	Page	Description`
- Columns must be separated by **TAB** characters (not spaces or commas)
- Empty titles are currently skipped by the script
- Titles are converted to uppercase for sorting but displayed as entered

---

## Validation Checklist

When testing the modernized script, verify:

### Output Format
- [ ] HTML structure matches original script output
- [ ] Section headers appear (Aa, Bb, Cc, etc.)
- [ ] Section headers only appear once per letter
- [ ] "Numbers & Special Characters" section for non-alphabetic entries
- [ ] Entries are properly formatted with title, book, page, description

### Sorting
- [ ] Case-insensitive alphabetical sorting
- [ ] Mixed case titles sort together (MiXeD/mixed)
- [ ] Numbers and symbols appear in separate section at end

### HTML Escaping
- [ ] `<script>` tags are escaped to `&lt;script&gt;`
- [ ] Quotes are properly handled
- [ ] Ampersands (`&`) are escaped to `&amp;`
- [ ] Less-than/greater-than symbols escaped

### Error Handling
- [ ] Empty titles are handled gracefully (skipped)
- [ ] Malformed rows don't crash the script
- [ ] Duplicates are both displayed (no silent dropping)

---

## Generating Test Output

### Option 1: Separate Output Files
```bash
python xenocrates.py test-data-minimal.tsv > output-minimal.html
python xenocrates.py test-data-basic.tsv > output-basic.html
python xenocrates.py test-data-edge-cases.tsv > output-edge-cases.html
```

### Option 2: With Enhanced CLI (Phase 3)
```bash
python xenocrates.py --output output-minimal.html test-data-minimal.tsv
python xenocrates.py --output output-basic.html test-data-basic.tsv
python xenocrates.py --output output-edge-cases.html test-data-edge-cases.tsv
```

---

## Regression Testing

To ensure the modernized script produces identical output to the original:

```bash
# Generate output from original script
python xenocrates-update-2018.py test-data-basic.tsv > original-output.html

# Generate output from modernized script
python xenocrates.py test-data-basic.tsv > modernized-output.html

# Compare outputs (should be identical)
diff original-output.html modernized-output.html
```

If there are differences, investigate whether they are:
- **Acceptable**: Improved HTML formatting, better escaping
- **Unacceptable**: Changed output structure, missing entries, incorrect sorting

---

## Adding New Test Cases

To add new test cases:

1. Open the appropriate TSV file in a text editor (NOT Excel - it may corrupt tabs)
2. Add a new line with tab-separated values: `Title[TAB]Book[TAB]Page[TAB]Description`
3. Save the file ensuring tabs are preserved
4. Run the script and verify output

**Tip**: Use `cat -A test-data-basic.tsv` to visualize tabs (shown as `^I`)

---

## Known Issues in Original Script

These issues should be addressed in the modernization:

1. **Bare except clause** (line 24): Silently swallows all errors including KeyError
2. **Empty title handling**: Script checks `if item[0] != ""` but empty titles still get appended to index
3. **No CSV parsing errors**: Malformed CSV lines are silently ignored
4. **Deprecated functions**: `cgi.escape()` doesn't escape quotes by default

---

## Test Data Maintenance

- Keep test data realistic (actual GIAC exam topics)
- Ensure all 26 letters are covered in `test-data-basic.tsv`
- Document any new edge cases added to `test-data-edge-cases.tsv`
- Update this README when adding new test files
