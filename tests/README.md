# Test Data and Sample Outputs

This directory contains test data files and sample HTML outputs for the Xenocrates index generator.

## Test Data Files

### Basic Tests
- **test-data-minimal.tsv** - Quick smoke test with 6 entries (A, B, C, Z, numbers, symbols)
- **test-data-basic.tsv** - Comprehensive test with 70+ entries covering all A-Z sections
- **test-data-csv.csv** - CSV format test (comma-delimited instead of tab)

### GSE (Multi-Course) Test
- **test-gse-with-course.tsv** - 5-column format with Course field for GSE exams

### Edge Case Tests
- **test-data-edge-cases.tsv** - HTML injection, special characters, duplicates, empty fields
- **test-lowercase-columns.tsv** - Case-insensitive column name matching
- **test-wrong-columns.tsv** - Column validation and error messages

## Sample Outputs

### Standard Format Output
**File:** `sample-output.html`
**Source:** Generated from `test-data-minimal.tsv`

This shows the standard 4-column output format:
```
{b-SEC401 / p-142}
```

**Preview:**
- Alphabetical section headers (Aa, Bb, Cc, Zz)
- Numbers & Special Characters section
- Blue titles with book/page references

### GSE Format Output
**File:** `sample-output-gse.html`
**Source:** Generated from `test-gse-with-course.tsv`

This shows the GSE 5-column output format with Course field:
```
{c-SEC575 / b-SEC505 / p-201}
```

**Preview:**
- Same structure as standard format
- Includes course number before book reference
- Useful for multi-course GSE certification exams

## How to View Sample Outputs

### In Browser
```bash
# Open sample output in your default browser
open tests/sample-output.html           # Mac
xdg-open tests/sample-output.html       # Linux
start tests/sample-output.html          # Windows

# View GSE format
open tests/sample-output-gse.html       # Mac
```

### Copy to Word
1. Open the HTML file in a browser
2. Press **CTRL + A** (or CMD + A on Mac) to select all
3. Copy and paste into Microsoft Word or Google Docs
4. Format as desired (2-column layout, adjust headers, etc.)

## Running Tests

### Generate Your Own Output
```bash
# Standard format
python3 xenocrates.py tests/test-data-minimal.tsv my-output.html

# GSE format
python3 xenocrates.py tests/test-gse-with-course.tsv my-gse-output.html

# Test error handling
python3 xenocrates.py tests/test-wrong-columns.tsv output.html
```

### Regenerate Sample Outputs
```bash
# Regenerate standard sample
python3 xenocrates.py tests/test-data-minimal.tsv tests/sample-output.html

# Regenerate GSE sample
python3 xenocrates.py tests/test-gse-with-course.tsv tests/sample-output-gse.html
```

## Expected Results

All tests should:
- ✅ Generate valid HTML output
- ✅ Sort entries alphabetically (case-insensitive)
- ✅ Create proper section headers (Aa-Zz)
- ✅ Escape HTML special characters (<, >, &, quotes)
- ✅ Handle duplicates (warn but include both)
- ✅ Skip empty titles (with warning)
- ✅ Auto-detect CSV vs TSV format

## What the Output Looks Like

When you open the HTML files in a browser, you'll see:

### Section Headers
Large bold headers for each letter:
- **Aa**, **Bb**, **Cc**, etc.
- **Numbers & Special Characters**

### Entry Format (Standard)
```
AES ENCRYPTION
{b-SEC401 / p-142}
Advanced Encryption Standard - 128/192/256 bit cipher
```

### Entry Format (GSE)
```
KERBEROS
{c-SEC575 / b-SEC505 / p-201}
Network authentication protocol
```

The blue titles and compact format make it easy to scan during exams!
