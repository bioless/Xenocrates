# Xenocrates

Xenocrates is an indexing tool for GIAC certification examinations. Creating an index with Xenocrates is a three-phase process involving: documentation/note-taking, sorting & normalization, and word processing.

**Version 2.0** - Modernized for Python 3, with support for multiple input formats (CSV/TSV/Excel/JSON) and enhanced features.

## Quick Start

```bash
# Modern usage (recommended)
python xenocrates.py notes.tsv index.html

# Supports multiple input formats
python xenocrates.py notes.csv index.html   # CSV format
python xenocrates.py notes.xlsx index.html  # Excel format
python xenocrates.py notes.json index.html  # JSON format

# Legacy mode (still supported)
python xenocrates.py notes.tsv > index.html
```

## Features

- ✅ **Python 3.8+** compatible
- ✅ **Multiple Input Formats** - CSV, TSV, Excel (.xlsx), JSON
- ✅ **GSE Support** - Optional Course column for multi-course indexes
- ✅ **Flexible Columns** - Case-insensitive, any order
- ✅ **Auto-detects format** - CSV, TSV, Excel, or JSON
- ✅ **Cross-platform** - Works on Mac, Windows, and Linux
- ✅ **HTML escaping** - Handles special characters safely
- ✅ **Smart Error Messages** - Typo suggestions and helpful hints
- ✅ **Duplicate detection** - Warns about duplicate entries
- ✅ **Alphabetical sorting** - Case-insensitive A-Z sections

## Video Tutorial

YouTube walkthrough: https://youtu.be/U4QmSQDIiHM

*Original tool provided by @0sm0s1z*

![Sample Output](docs/sample2.jpg)


## Indexing Methodology

### 1. Create Your Study Notes Spreadsheet

Create an Excel or Google Sheets spreadsheet with these columns:

**Standard Format (4 columns):**
| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| **Title** | ✅ Yes | Term or topic name | `AES Encryption` |
| **Description** | ✅ Yes | Detailed explanation | `Advanced Encryption Standard - 128/192/256 bit cipher` |
| **Page** | ✅ Yes | Page number reference | `142` |
| **Book** | ✅ Yes | Course/book identifier | `SEC401` |

**GSE Format (5 columns for multi-course exams):**
| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| **Title** | ✅ Yes | Term or topic name | `Kerberos` |
| **Description** | ✅ Yes | Detailed explanation | `Network authentication protocol` |
| **Page** | ✅ Yes | Page number reference | `201` |
| **Book** | ✅ Yes | Book identifier | `SEC505` |
| **Course** | 📘 Optional | Course number (for GSE) | `SEC575` |

**Tips:**
- Column names are **case-insensitive** ('title' = 'Title' = 'TITLE')
- **Columns can be in any order** - the script reads by name, not position
- Take notes as you study - add a "." in Description if you just need the reference
- Don't worry about sorting - Xenocrates handles that automatically
- Special characters are handled safely (quotes, <, >, &, etc.)

### 2. Save in a Supported Format

Xenocrates supports multiple input formats. Choose the one that works best for your workflow:

**Option A - Excel (Recommended for most users):**
- Keep your spreadsheet as Excel format (.xlsx)
- No export needed! Use the file directly
- `python xenocrates.py notes.xlsx index.html`

**Option B - Tab-delimited (TSV):**
- Excel: File → Save As → Tab Delimited Text (.txt or .tsv)
- Google Sheets: File → Download → Tab-separated values (.tsv)

**Option C - Comma-delimited (CSV):**
- Excel: File → Save As → CSV (Comma delimited) (.csv)
- Google Sheets: File → Download → Comma-separated values (.csv)

**Option D - JSON (For automation/scripting):**
- Create programmatically or export from tools
- Format: `{"entries": [{"Title": "...", "Description": "...", "Page": "...", "Book": "..."}]}`

**Note:** Xenocrates auto-detects the format and delimiter, so all formats work seamlessly!

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
- For CSV/TSV/JSON: No external dependencies (uses Python standard library)
- For Excel (.xlsx): Requires `openpyxl` library

**Check your Python version:**
```bash
python3 --version
```

**Get the script:**
```bash
# Clone the repository
git clone https://github.com/bioless/Xenocrates.git
cd Xenocrates

# Install Excel support (optional, only needed for .xlsx files)
pip install -r requirements.txt
# OR: pip install openpyxl

# Make executable (Linux/Mac)
chmod +x xenocrates.py

# Run it
python3 xenocrates.py --help
```

**Note:** If you only use CSV/TSV/JSON files, you don't need to install openpyxl. The script will show a helpful error message if you try to read an Excel file without it.

---

## Legacy Scripts (Archived)

The following scripts have been archived in the `archive/` directory:

- `archive/xenocrates.py` - Original Python 2 version
- `archive/xenocrates-gse.py` - GSE-specific variant with course column
- `archive/xenocrates-update-2018.py` - 2018 update (Python 2)

These are kept for reference but are **no longer maintained**. Please use the new `xenocrates.py` (version 2.0+).

**Migration Note:** The new version supports **both** 4-column and 5-column formats:
- **Standard**: Title, Description, Page, Book (output: `{b-SEC401 / p-142}`)
- **GSE**: Title, Description, Page, Book, Course (output: `{c-SEC575 / b-SEC505 / p-201}`)

The Course column is now **optional** and auto-detected. Old xenocrates-gse.py files work perfectly!

---

## Examples

### Example 1: Excel Format (Recommended)
```bash
# Create your notes in Excel with columns: Title, Book, Page, Description
# Keep as .xlsx - no need to export!
python3 xenocrates.py notes.xlsx index.html
```

### Example 2: TSV Format
```bash
# Traditional tab-delimited format
python3 xenocrates.py notes.tsv index.html
```

### Example 3: CSV Format
```bash
# Comma-delimited format
python3 xenocrates.py notes.csv index.html
```

### Example 4: JSON Format
```bash
# JSON format (great for automation)
python3 xenocrates.py notes.json index.html
```

**JSON format example:**
```json
{
  "entries": [
    {
      "Title": "AES Encryption",
      "Description": "Advanced Encryption Standard - 128/192/256 bit cipher",
      "Page": "142",
      "Book": "SEC401"
    },
    {
      "Title": "Kerberos",
      "Description": "Network authentication protocol",
      "Page": "201",
      "Book": "SEC505",
      "Course": "SEC575"
    }
  ]
}
```

### Example 5: GSE Multi-Course Index
```bash
# For GSE exams covering multiple courses
# Use 5 columns: Title, Description, Page, Book, Course
# Works with any format (Excel, CSV, TSV, JSON)
python3 xenocrates.py gse-notes.xlsx gse-index.html

# Output will show: {c-SEC575 / b-SEC505 / p-201}
```

### Example 6: Check Output
```bash
# Generate index
python3 xenocrates.py notes.xlsx index.html

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
Required: Title, Description, Page, Book

Suggestions:
  'Desc' → Did you mean 'Description'?

Note: Column names are case-insensitive
      Columns can be in any order
```

**Solution:** Ensure your spreadsheet has all 4 required columns: Title, Description, Page, Book. Column names are case-insensitive and can be in any order. Check the suggestions for typo fixes.

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
- ✅ **Multiple input formats** - CSV, TSV, Excel (.xlsx), JSON
- ✅ **Excel support** - Use .xlsx files directly, no export needed
- ✅ **JSON support** - Great for automation and programmatic generation
- ✅ **GSE Support** - Optional Course column for multi-course indexes
- ✅ **Case-insensitive columns** - 'title' = 'Title' = 'TITLE'
- ✅ **Flexible column order** - Columns can be in any order
- ✅ **Smart error messages** - Typo suggestions like 'Titel' → 'Title'
- ✅ **Format auto-detection** - Automatically detects CSV, TSV, Excel, or JSON
- ✅ **Direct file output** - No more `> index.html` redirection
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

