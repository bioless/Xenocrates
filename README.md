# Xenocrates

Xenocrates is an indexing tool for GIAC certification examinations. Creating an index with Xenocrates is a three-phase process involving: documentation/note-taking, sorting & normalization, and word processing.

**Version 2.0** - Modernized for Python 3, with CSV/TSV auto-detection and enhanced features.

## Quick Start

```bash
# Modern usage (recommended)
python xenocrates.py notes.tsv index.html

# Also supports CSV files
python xenocrates.py notes.csv index.html

# Legacy mode (still supported)
python xenocrates.py notes.tsv > index.html
```

## Features

- ✅ **Python 3.8+** compatible
- ✅ **Auto-detects CSV or TSV** format (tab or comma delimited)
- ✅ **Cross-platform** - Works on Mac, Windows, and Linux
- ✅ **HTML escaping** - Handles special characters safely
- ✅ **Duplicate detection** - Warns about duplicate entries
- ✅ **Validation** - Clear error messages for malformed files
- ✅ **Alphabetical sorting** - Case-insensitive A-Z sections

## Video Tutorial

YouTube walkthrough: https://youtu.be/U4QmSQDIiHM

*Original tool provided by @0sm0s1z*

![Sample Output](sample2.jpg)


## Indexing Methodology

### 1. Create Your Study Notes Spreadsheet

Create an Excel or Google Sheets spreadsheet with these **required columns**:

| Column | Description | Example |
|--------|-------------|---------|
| **Title** | Term or topic name | `AES Encryption` |
| **Book** | Course/book identifier | `SEC401` |
| **Page** | Page number reference | `142` |
| **Description** | Detailed explanation | `Advanced Encryption Standard - 128/192/256 bit symmetric cipher` |

**Tips:**
- Column names are **case-sensitive** (must be: Title, Book, Page, Description)
- Take notes as you study - add a "." in Description if you just need the reference
- Don't worry about sorting - Xenocrates handles that automatically
- Special characters are handled safely (quotes, <, >, &, etc.)

### 2. Save as TSV or CSV

**Option A - Tab-delimited (TSV):**
- Excel: File → Save As → Tab Delimited Text (.txt or .tsv)
- Google Sheets: File → Download → Tab-separated values (.tsv)

**Option B - Comma-delimited (CSV):**
- Excel: File → Save As → CSV (Comma delimited) (.csv)
- Google Sheets: File → Download → Comma-separated values (.csv)

**Note:** Xenocrates auto-detects the delimiter, so either format works!

### 3. Generate the HTML Index

```bash
# Modern usage - direct file output
python xenocrates.py my-notes.tsv index.html

# Check for help
python xenocrates.py --help

# Check version
python xenocrates.py --version
```

The script will:
- Auto-detect CSV or TSV format
- Sort entries alphabetically (case-insensitive)
- Create section headers (Aa, Bb, Cc, etc.)
- Escape special characters safely
- Warn about duplicates and empty entries

### 4. Format in Word Processor

Xenocrates has created an HTML file with the formatted content of your index:

1. Open `index.html` in a web browser
2. Press **CTRL + A** (or CMD + A on Mac) to select all content
3. Copy and paste into Microsoft Word or Google Docs

### 5. Customize Document Formatting

Format the document according to your preferences:

- **Two-column layout** - Easier to scan and saves paper
- **Even pages per section** - Important for double-sided printing and binding
- **Letter header styling** - Use Word's "Title" style for Aa, Bb, Cc headers
- **Cover sheet** - Add date and course information

### 6. Print and Bind

Print and take to OfficeMax/Staples/FedEx for binding:

- **Recommended binding**: Clear front cover + black back cover
- **Pro tip**: Use clear covers on both sides if you want to bind a quick-reference sheet to the back (like SANS packet header cheatsheet)
- **Page count**: Ensure even number of pages per section for proper double-sided binding

### 7. Take Your Exam

- Bring your index to the exam
- Use it as a reference during the test
- Get certified!

---

## Installation & Requirements

**Requirements:**
- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

**Check your Python version:**
```bash
python3 --version
```

**Get the script:**
```bash
# Clone the repository
git clone https://github.com/bioless/Xenocrates.git
cd Xenocrates

# Make executable (Linux/Mac)
chmod +x xenocrates.py

# Run it
python3 xenocrates.py --help
```

---

## Legacy Scripts (Archived)

The following scripts have been archived in the `archive/` directory:

- `archive/xenocrates.py` - Original Python 2 version
- `archive/xenocrates-gse.py` - GSE-specific variant with course column
- `archive/xenocrates-update-2018.py` - 2018 update (Python 2)

These are kept for reference but are **no longer maintained**. Please use the new `xenocrates.py` (version 2.0+).

**Migration Note:** The new version uses 4 columns (Title, Book, Page, Description) instead of 5. The "Course" column from xenocrates-gse.py is no longer needed.

---

## Examples

### Example 1: Basic Usage
```bash
# Create your notes in Excel with columns: Title, Book, Page, Description
# Save as notes.tsv
python3 xenocrates.py notes.tsv index.html
```

### Example 2: CSV Format
```bash
# Save as CSV from Excel
python3 xenocrates.py notes.csv index.html
```

### Example 3: Check Output
```bash
# Generate index
python3 xenocrates.py notes.tsv index.html

# Open in browser
open index.html  # Mac
xdg-open index.html  # Linux
start index.html  # Windows
```

---

## Troubleshooting

### "Missing required columns" Error
```
Error: Missing required columns: Description
Found columns: Title, Book, Page
Required: Title, Book, Page, Description
```

**Solution:** Ensure your spreadsheet has all 4 required columns with exact names (case-sensitive).

### "File not found" Error
```
Error: File 'notes.tsv' not found
```

**Solution:** Check the file path. Use `ls` (Mac/Linux) or `dir` (Windows) to list files.

### Special Characters Look Wrong
**Solution:** The script automatically escapes HTML characters. If you see `&lt;` or `&gt;`, this is correct - it will display properly when pasted into Word.

### Duplicates Warning
```
Warning: Found 2 duplicate entries (same title/book/page):
  - 'Firewall' (Book: SEC503, Page: 45) on rows: 10, 25
```

**Solution:** This is informational. Both entries will be included in the output. Review your notes to see if duplicates are intentional.

---

## What's New in Version 2.0

- ✅ **Python 3.8+ support** (Python 2 no longer supported)
- ✅ **CSV auto-detection** - No need to specify delimiter
- ✅ **Direct file output** - No more `> index.html` redirection
- ✅ **Better error messages** - Clear validation and helpful tips
- ✅ **Duplicate detection** - Warns about duplicate entries
- ✅ **Cross-platform** - Works on Mac, Windows, Linux
- ✅ **HTML escaping** - Safe handling of special characters
- ✅ **Help and version flags** - `--help` and `--version`

---

## License

Original tool by @0sm0s1z. Modernization updates by community contributors.

---

## Contributing

Found a bug? Have a suggestion? Please open an issue on GitHub!

