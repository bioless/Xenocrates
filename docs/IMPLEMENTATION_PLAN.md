# Xenocrates ISO 999 & Chicago Manual of Style Enhancement Plan

**Version**: 2.1-2.3 Roadmap
**Author**: Claude AI Assistant
**Date**: 2026-01-13
**Branch**: `claude/review-output-formatting-89bgT`

---

## Executive Summary

This document outlines a comprehensive implementation plan to enhance Xenocrates with professional indexing standards based on **ISO 999:1996** (Information and documentation — Guidelines for the content, organization and presentation of indexes) and **Chicago Manual of Style (18th Edition)** indexing best practices.

### Goals

1. **Improve index usability** for exam reference through better formatting and organization
2. **Adopt industry standards** (ISO 999, Chicago Manual) for professional-grade indexes
3. **Maintain backward compatibility** with existing user workflows and data files
4. **Preserve simplicity** while adding powerful optional features

### Phased Approach

- **Phase 1** (Week 1): Foundation features - compact mode, page ranges, grouping
- **Phase 2** (Week 2): Advanced references - cross-references, primary marking, categories
- **Phase 3** (Week 3): Automation - duplicate merging, alt sorts, acronym detection

---

## Current Architecture (v2.0 with Excel/JSON)

### Code Structure

**File**: `xenocrates.py` (817 lines post Excel/JSON merge)

**Key Components**:

1. **Input Layer** (Lines 36-638)
   - `detect_file_format()` - Auto-detect format from extension
   - `read_csv_data()` - Parse CSV/TSV files
   - `read_excel_data()` - Parse Excel (.xlsx) files
   - `read_json_data()` - Parse JSON files
   - `read_input_file()` - Unified entry point dispatcher

2. **Validation Layer** (Lines 98-237)
   - `normalize_column_names()` - Case-insensitive column matching
   - `validate_columns()` - Required column checks with suggestions
   - `suggest_column_fix()` - Typo correction suggestions

3. **Data Model** (Current)
   ```python
   # List of entries
   index = [
       ['TITLE_UPPER', 'description', 'page', 'book', 'course'],
       ...
   ]

   # Return format
   (index_data, has_course_column)
   ```

4. **Output Layer** (Lines 641-817)
   - `get_section_header()` - Generate section headers (Aa, Bb, Cc...)
   - `print_entry_to_file()` - Format individual entries
   - `generate_index()` - Main processing and output generation

### Current Features

✅ Multiple input formats (CSV, TSV, Excel, JSON)
✅ GSE support with optional Course column
✅ Case-insensitive, flexible column ordering
✅ HTML escaping for security
✅ Duplicate detection (warnings only)
✅ Alphabetical sorting with section headers

---

## Standards-Based Design Rationale

### ISO 999:1996 Compliance

| Standard | Description | Implementation Phase |
|----------|-------------|---------------------|
| **§6.3** | Alphabetization methods | ✅ Current (case-insensitive A-Z) |
| **§7.3** | Hierarchical structure | Phase 2.3 (Categories) |
| **§8** | Locator formatting | Phase 1.2 (Page ranges) |
| **§9** | Cross-references | Phase 2.1 (SeeAlso) |
| **§9.2** | Grouping by source | Phase 1.3 (Grouping) |

### Chicago Manual of Style (18th Ed)

| Section | Description | Implementation Phase |
|---------|-------------|---------------------|
| **16.9-16.14** | Locator conventions | Phase 1.2, 2.2 |
| **16.15-16.23** | Cross-references | Phase 2.1 |
| **16.16** | Bold primary references | Phase 2.2 |
| **16.27-16.29** | Hierarchical indexing | Phase 2.3 |
| **16.32** | Acronym handling | Phase 3.3 |

---

## Phase 1: Foundation Features (Week 1)

**Goal**: High-impact improvements with minimal risk
**Breaking Changes**: Grouping changes output format (opt-out available)
**Release**: v2.1.0

### 1.1: Compact Output Mode

**Priority**: ⭐⭐⭐ High
**Complexity**: Low
**Timeline**: 1-2 days

**Rationale**: ISO 999 recommends different formatting densities based on index purpose. Compact mode reduces whitespace for exam quick-reference; detailed mode (current) for study materials.

**Implementation**:

```bash
# New command-line flag
python xenocrates.py notes.tsv index.html --format=compact
python xenocrates.py notes.tsv index.html --format=detailed  # default
```

**Changes Required**:

1. **Add argparse argument** (in `main()` function, ~line 750):
   ```python
   parser.add_argument(
       '--format',
       choices=['compact', 'detailed'],
       default='detailed',
       help='Output format: compact (dense) or detailed (spacious, default)'
   )
   ```

2. **Modify `get_section_header()`** (~line 641):
   ```python
   def get_section_header(character, format='detailed'):
       # Reduce font size for compact mode
       font_size = '36.0pt' if format == 'compact' else '45.0pt'

       # Reduce spacing for compact mode
       spacing = '<br>' if format == 'compact' else '<br><br>'
   ```

3. **Modify `print_entry_to_file()`** (~line 683):
   ```python
   def print_entry_to_file(title, description, page, book, course, output, format='detailed'):
       # Adjust spacing between entries based on format
       # Compact: minimal spacing
       # Detailed: current spacing
   ```

4. **Update `generate_index()`** to pass format parameter

**Files Modified**:
- `xenocrates.py` (~50 lines changed/added)

**Testing**:
- Create `tests/test-compact-format.sh` comparison script
- Generate both formats with `test-data-basic.tsv`
- Verify rendering in Word and Google Docs
- Measure page count reduction (target: 20-30%)

**Backward Compatibility**: 100% - defaults to current behavior

---

### 1.2: Page Range Support

**Priority**: ⭐⭐⭐ High
**Complexity**: Low
**Timeline**: 1-2 days

**Rationale**: Chicago Manual 16.12 recommends page ranges for topics spanning multiple pages. Reduces entry duplication and improves scannability.

**Implementation**:

**Input formats supported**:
```
Title           | Page
Single Page     | 142
Hyphen Range    | 142-147
En-dash Range   | 142–147
Multiple Pages  | 142, 156, 201
Complex         | 10-15, 25-30, 42
```

**Normalization**:
- Convert all dashes to en-dash (–) for consistency
- Preserve commas for multiple distinct references
- Validate ranges (warn if end < start)
- Sort by first page number

**Changes Required**:

1. **Add `normalize_page_range()` function** (after line 237):
   ```python
   def normalize_page_range(page_str):
       """
       Normalize page numbers and ranges to standard format.

       Handles: "142", "142-147", "142, 156", "10-15, 25-30"

       Args:
           page_str: Page number or range string

       Returns:
           Tuple of (normalized_string, first_page_number)
       """
       # Replace various dash types with en-dash
       page_str = page_str.replace('—', '–').replace('-', '–')

       # Validate ranges (e.g., 147-142 is invalid)
       # Extract first page number for sorting
       # Return normalized string and sort key
   ```

2. **Update `read_csv_data()`** (~line 239):
   ```python
   # After reading page field
   page, sort_page = normalize_page_range(row[columns['Page']])
   ```

3. **Update data model to include sort key**:
   ```python
   # Store: [title_upper, description, page_display, page_sort, book, course]
   ```

4. **Update sorting logic** to use `page_sort` field

**Files Modified**:
- `xenocrates.py` (~80 lines added, 30 modified)

**Testing**:
- Create `tests/test-page-ranges.tsv` with various formats
- Test sorting with ranges (142-147 sorts before 200)
- Test edge cases: invalid ranges, non-numeric pages
- Verify Word rendering maintains en-dash

**Backward Compatibility**: 100% - single pages work unchanged

---

### 1.3: Group Multiple References by Title

**Priority**: ⭐⭐⭐ High
**Complexity**: Medium (data structure refactor)
**Timeline**: 2-3 days

**Rationale**: ISO 999 Section 9.2 recommends consolidating references to the same term. Currently, duplicate titles are scattered; grouping improves organization and reduces cognitive load.

**Current Output** (scattered duplicates):
```
FIREWALL
{b-SEC401 / p-142}
Packet filtering device

[... other entries ...]

FIREWALL
{b-SEC503 / p-89}
Network security appliance
```

**New Output** (grouped):
```
FIREWALL
  {b-SEC401 / p-142} Packet filtering device
  {b-SEC503 / p-89} Network security appliance
```

**Implementation**:

**Data Model Change** (this is the key refactor):

```python
# OLD (v2.0): List of entries
index = [
    ['TITLE_UPPER', 'description', 'page', 'book', 'course'],
    ...
]

# NEW (v2.1): Dictionary grouped by title
index = {
    'TITLE_UPPER': [
        {
            'description': 'Packet filtering device',
            'page': '142',
            'page_sort': 142,
            'book': 'SEC401',
            'course': ''
        },
        {
            'description': 'Network security appliance',
            'page': '89',
            'page_sort': 89,
            'book': 'SEC503',
            'course': ''
        }
    ],
    ...
}
```

**Changes Required**:

1. **Refactor `read_csv_data()`** (~line 239):
   ```python
   def read_csv_data(filename):
       # ... existing validation ...

       # NEW: Use dict instead of list
       index = defaultdict(list)  # Already imported from collections

       for row in reader:
           # ... existing parsing ...

           # Group by title
           index[title_upper].append({
               'description': description,
               'page': page_normalized,
               'page_sort': page_sort_key,
               'book': book,
               'course': course
           })

       # Sort references within each title group by: course, book, page
       for title in index:
           index[title].sort(key=lambda r: (r['course'], r['book'], r['page_sort']))

       return dict(index), has_course_column
   ```

2. **Update `read_excel_data()`** (~line 351) - same pattern
3. **Update `read_json_data()`** (~line 479) - same pattern

4. **Refactor `generate_index()`** (~line 720):
   ```python
   def generate_index(filename, output_file, format='detailed'):
       # Read returns dict now
       index, has_course_column = read_input_file(filename)

       # Sort titles alphabetically
       sorted_titles = sorted(index.keys())

       current_section = None
       for title in sorted_titles:
           # Get first character for section headers
           first_char = title[0] if title else ''

           # Print section header if changed
           section_num, header_html = get_section_header(first_char, format)
           if section_num != current_section:
               print(header_html, file=output)
               current_section = section_num

           # Print title once
           title_escaped = html.escape(title, quote=True)
           print(f"<span class=topic><b><span style='color:blue'> {title_escaped} </span></b></span>", file=output)

           # Print all references for this title
           for ref in index[title]:
               print_reference(ref, has_course_column, output, format)
   ```

5. **Add `print_reference()` helper function**:
   ```python
   def print_reference(ref, has_course_column, output, format='detailed'):
       """Print a single reference within a grouped entry."""
       # Build reference string: {c-575 / b-SEC401 / p-142}
       # Print description
       # Add spacing based on format
   ```

6. **Update duplicate detection** (now intentional, not warning):
   ```python
   # Instead of warning, report grouping statistics
   print(f"Info: Grouped {total_refs} references into {len(index)} unique entries", file=sys.stderr)
   ```

**Files Modified**:
- `xenocrates.py` (~200 lines modified, 80 added)

**Testing**:
- Create `tests/test-grouping.tsv` with intentional duplicates
- Test with all input formats (CSV, TSV, Excel, JSON)
- Verify correct sort order within groups
- Test edge cases: single ref vs multiple refs
- Verify GSE mode grouping (course + book + page)

**Backward Compatibility**: ⚠️ **Output format changes**
- Old files work (no input changes required)
- Output looks different (improved, but different)
- Add `--no-grouping` flag to restore old behavior temporarily

**Migration Strategy**:
```python
# Add flag for transition period
parser.add_argument(
    '--no-grouping',
    action='store_true',
    help='Disable grouping (legacy behavior)'
)

# If --no-grouping, convert dict back to list format
if args.no_grouping:
    index = flatten_index(index)  # Helper to restore old structure
```

---

## Phase 2: Advanced References (Week 2)

**Goal**: Professional-grade cross-references and hierarchical organization
**Breaking Changes**: Optional columns (backward compatible)
**Release**: v2.2.0

### 2.1: Cross-Reference Support

**Priority**: ⭐⭐ Medium
**Complexity**: Medium
**Timeline**: 1-2 days

**Rationale**: ISO 999 Section 10 and Chicago Manual 16.18-16.23 require cross-references for related terms, synonyms, and hierarchical relationships. Critical for exam usability.

**Implementation**:

**New optional column**: `SeeAlso`

**Input format**:
```
Title     | Description              | Page | Book   | SeeAlso
Firewall  | Packet filtering device  | 142  | SEC401 | IDS, IPS, ACL
IDS       | Intrusion Detection      | 89   | SEC503 | Firewall, SIEM
```

**Output format**:
```
FIREWALL
  {b-SEC401 / p-142} Packet filtering device
  See also: IDS, IPS, ACL

IDS
  {b-SEC503 / p-89} Intrusion Detection System
  See also: Firewall, SIEM
```

**Changes Required**:

1. **Update `normalize_column_names()`** (~line 98):
   ```python
   standard_names = {
       "title": "Title",
       "book": "Book",
       "page": "Page",
       "description": "Description",
       "course": "Course",
       "seealso": "SeeAlso",  # NEW
   }
   ```

2. **Update data model** to include `seealso`:
   ```python
   index[title_upper].append({
       'description': description,
       'page': page_normalized,
       'page_sort': page_sort_key,
       'book': book,
       'course': course,
       'seealso': parse_seealso(row.get('SeeAlso', ''))  # NEW
   })
   ```

3. **Add `parse_seealso()` function**:
   ```python
   def parse_seealso(seealso_str):
       """
       Parse comma-separated see-also references.

       Returns list of uppercased terms for matching.
       """
       if not seealso_str:
           return []

       # Split by comma, strip whitespace, uppercase
       refs = [r.strip().upper() for r in seealso_str.split(',')]
       return [r for r in refs if r]  # Filter empty
   ```

4. **Add validation** (warn if SeeAlso references non-existent entry):
   ```python
   def validate_cross_references(index):
       """Warn about broken cross-references."""
       all_titles = set(index.keys())

       for title, refs in index.items():
           for ref in refs:
               for see_title in ref.get('seealso', []):
                   if see_title not in all_titles:
                       print(f"Warning: '{title}' references non-existent entry '{see_title}'",
                             file=sys.stderr)
   ```

5. **Update `print_reference()`** to output cross-refs:
   ```python
   # After description
   if ref.get('seealso'):
       seealso_list = ', '.join(ref['seealso'])
       print(f"<br><i>See also: {html.escape(seealso_list)}</i>", file=output)
   ```

**Files Modified**:
- `xenocrates.py` (~100 lines added)

**Testing**:
- Create `tests/test-cross-references.tsv`
- Test circular references (A → B → A)
- Test broken references (warns but continues)
- Test empty SeeAlso column (ignored)
- Verify italic rendering in Word

**Backward Compatibility**: 100% - SeeAlso column is optional

---

### 2.2: Primary Reference Marking

**Priority**: ⭐⭐ Medium
**Complexity**: Low
**Timeline**: 1 day

**Rationale**: Chicago Manual 16.16 recommends bolding primary/definitive references to help readers identify the most important page quickly.

**Implementation**:

**New optional column**: `Primary`

**Input format**:
```
Title     | Description              | Page | Book   | Primary
Firewall  | Main definition          | 142  | SEC401 | TRUE
Firewall  | Brief mention            | 89   | SEC503 | FALSE
```

**Output format** (page 142 in bold):
```
FIREWALL
  {b-SEC401 / p-142} Main definition          [142 bold]
  {b-SEC503 / p-89} Brief mention             [89 normal]
```

**Changes Required**:

1. **Update `normalize_column_names()`**:
   ```python
   "primary": "Primary",  # NEW
   ```

2. **Add `parse_boolean()` utility**:
   ```python
   def parse_boolean(value):
       """Parse various boolean representations."""
       if isinstance(value, bool):
           return value

       val_str = str(value).strip().lower()
       return val_str in ('true', '1', 'yes', 'y')
   ```

3. **Update data model**:
   ```python
   'primary': parse_boolean(row.get('Primary', '')),  # NEW
   ```

4. **Add validation** (warn if multiple primaries for same title):
   ```python
   def validate_primary_refs(index):
       """Warn about multiple primary references for same title."""
       for title, refs in index.items():
           primary_count = sum(1 for r in refs if r.get('primary'))
           if primary_count > 1:
               print(f"Warning: '{title}' has {primary_count} primary references (expected 1)",
                     file=sys.stderr)
   ```

5. **Update `print_reference()`** to bold page if primary:
   ```python
   # Build page reference
   page_display = f"<b>{page_escaped}</b>" if ref.get('primary') else page_escaped
   ref_str = f"{{c-{course_escaped} / b-{book_escaped} / p-{page_display}}}"
   ```

**Files Modified**:
- `xenocrates.py` (~60 lines added)

**Testing**:
- Create `tests/test-primary-refs.tsv`
- Test all boolean formats (TRUE, true, 1, yes, Y)
- Test multiple primaries (should warn)
- Verify bold renders in Word

**Backward Compatibility**: 100% - Primary column is optional

---

### 2.3: Hierarchical Categories

**Priority**: ⭐⭐ Medium
**Complexity**: High
**Timeline**: 2-3 days

**Rationale**: ISO 999 Section 8 and Chicago Manual 16.27-16.29 recommend hierarchical organization for complex indexes. Groups related terms under parent categories.

**Implementation**:

**New optional column**: `Category`

**Input format**:
```
Title | Description      | Page | Book   | Category
AES   | Symmetric cipher | 142  | SEC401 | Cryptography > Symmetric
RSA   | Asymmetric       | 201  | SEC401 | Cryptography > Asymmetric
DES   | Legacy cipher    | 89   | SEC401 | Cryptography > Symmetric
```

**Output format** (indented hierarchy):
```
CRYPTOGRAPHY
  Asymmetric
    RSA
    {b-SEC401 / p-201}
    Asymmetric encryption cipher

  Symmetric
    AES
    {b-SEC401 / p-142}
    Symmetric encryption cipher

    DES
    {b-SEC401 / p-89}
    Legacy cipher
```

**Changes Required**:

1. **Update `normalize_column_names()`**:
   ```python
   "category": "Category",  # NEW
   ```

2. **Add `parse_category()` function**:
   ```python
   def parse_category(category_str):
       """
       Parse hierarchical category string.

       Format: "Main > Sub > SubSub"

       Returns: tuple of category levels
       """
       if not category_str:
           return ()

       levels = [l.strip().upper() for l in category_str.split('>')]
       return tuple(levels)
   ```

3. **Update data structure** to include category at title level:
   ```python
   # Reorganize data model to group by category first
   {
       ('CRYPTOGRAPHY', 'SYMMETRIC'): {
           'AES': [...],
           'DES': [...]
       },
       ('CRYPTOGRAPHY', 'ASYMMETRIC'): {
           'RSA': [...]
       },
       (): {  # No category
           'FIREWALL': [...]
       }
   }
   ```

4. **Add `print_category_header()` function**:
   ```python
   def print_category_header(category_levels, output, format='detailed'):
       """Print hierarchical category headers with indentation."""
       for i, level in enumerate(category_levels):
           indent = '  ' * i  # Increase indentation per level
           # Print level header
   ```

5. **Major refactor of `generate_index()`**:
   ```python
   def generate_index(filename, output_file, format='detailed', enable_categories=False):
       index, has_course_column = read_input_file(filename)

       if enable_categories:
           # Group by category first
           categorized = group_by_category(index)
           # Sort by category, then title
           # Print with category headers and indentation
       else:
           # Current alphabetical behavior
   ```

**Files Modified**:
- `xenocrates.py` (~150 lines added, 50 modified)

**Testing**:
- Create `tests/test-categories.tsv` with 2-3 level hierarchies
- Test mixed (some with categories, some without)
- Test edge case: same title in different categories
- Verify indentation renders correctly in Word
- Test with `--enable-categories` flag

**Backward Compatibility**: 100% - Category column is optional, feature requires flag initially

**Migration Note**: Consider making this opt-in via flag in v2.2, then default-enabled in v2.3 if stable.

```python
parser.add_argument(
    '--enable-categories',
    action='store_true',
    help='Enable hierarchical category organization (experimental)'
)
```

---

## Phase 3: Automation & Flexibility (Week 3)

**Goal**: Advanced automation and alternative workflows
**Breaking Changes**: All opt-in features
**Release**: v2.3.0

### 3.1: Duplicate Consolidation

**Priority**: ⭐ Low
**Complexity**: Low
**Timeline**: 1 day

**Rationale**: Currently warns about true duplicates (same title/book/page) but includes both. ISO 999 recommends merging when content is identical.

**Implementation**:

```bash
# Opt-in flag
python xenocrates.py notes.tsv index.html --merge-duplicates
```

**Current behavior** (warnings):
```
Warning: Found 1 duplicate entries:
  - 'FIREWALL' (Book: SEC401, Page: 142) on rows: 10, 25
```

**New behavior** (auto-merge):
```
Info: Merged 1 duplicate entries:
  - 'FIREWALL' (Book: SEC401, Page: 142) - combined descriptions
```

**Merge logic**:
- Same title + book + page + course = duplicate
- Keep first occurrence
- Combine descriptions if different:
  - Desc 1: "Packet filter"
  - Desc 2: "Network security device"
  - Result: "Packet filter; Network security device"

**Changes Required**:

1. **Add `--merge-duplicates` flag**:
   ```python
   parser.add_argument(
       '--merge-duplicates',
       action='store_true',
       help='Automatically merge duplicate entries (same title/book/page)'
   )
   ```

2. **Add `merge_descriptions()` function**:
   ```python
   def merge_descriptions(desc1, desc2):
       """Intelligently combine two descriptions."""
       if desc1 == desc2:
           return desc1  # Identical

       # Combine with semicolon separator
       return f"{desc1}; {desc2}"
   ```

3. **Update duplicate detection** in `read_*_data()`:
   ```python
   # Check for duplicate refs in same title group
   for i, ref in enumerate(index[title_upper]):
       if ref matches new_ref on (book, page, course):
           if merge_duplicates:
               # Merge descriptions
               ref['description'] = merge_descriptions(ref['description'], new_ref['description'])
               merged_count += 1
           else:
               # Warn (current behavior)
               warn_duplicate()
   ```

**Files Modified**:
- `xenocrates.py` (~50 lines added/modified)

**Testing**:
- Use existing `tests/test-data-edge-cases.tsv` (has duplicates)
- Test identical descriptions (should not duplicate text)
- Test different descriptions (should combine with semicolon)
- Test without flag (should warn, not merge)

**Backward Compatibility**: 100% - requires opt-in flag

---

### 3.2: Alternative Sort Orders

**Priority**: ⭐ Low
**Complexity**: Medium
**Timeline**: 2 days

**Rationale**: Different use cases require different organizations. Linear reading benefits from page-order; section-by-section study benefits from book-order.

**Implementation**:

```bash
# Sort modes
python xenocrates.py notes.tsv index.html --sort-by=title     # default
python xenocrates.py notes.tsv index.html --sort-by=book      # by course material
python xenocrates.py notes.tsv index.html --sort-by=page      # linear order
python xenocrates.py notes.tsv index.html --sort-by=category  # requires categories
```

**Output examples**:

**By Book** (study section-by-section):
```
=== SEC401 ===
AES ENCRYPTION {p-142} ...
FIREWALL {p-89} ...

=== SEC503 ===
DNS TUNNELING {p-167} ...
IDS {p-89} ...
```

**By Page** (linear reading):
```
PAGE 89
  FIREWALL {b-SEC401} ...
  IDS {b-SEC503} ...

PAGE 142
  AES ENCRYPTION {b-SEC401} ...
```

**Changes Required**:

1. **Add `--sort-by` argument**:
   ```python
   parser.add_argument(
       '--sort-by',
       choices=['title', 'book', 'page', 'category'],
       default='title',
       help='Sort order: title (default), book, page, or category'
   )
   ```

2. **Add sort functions**:
   ```python
   def sort_by_book(index):
       """Group entries by book, then alphabetical."""
       # Reorganize data structure
       # Return: {book: {title: [refs]}}

   def sort_by_page(index):
       """Group entries by page number."""
       # Return: {page: {title: [refs]}}

   def sort_by_category(index):
       """Group entries by category (requires Category column)."""
       # Return existing category structure
   ```

3. **Update `generate_index()`**:
   ```python
   def generate_index(filename, output_file, format='detailed', sort_by='title', ...):
       index, has_course_column = read_input_file(filename)

       if sort_by == 'book':
           organized = sort_by_book(index)
           print_by_book(organized, output, format)
       elif sort_by == 'page':
           organized = sort_by_page(index)
           print_by_page(organized, output, format)
       # ... etc
   ```

4. **Add section headers for book/page groupings**:
   ```python
   def print_book_header(book, output):
       """Print book section header."""
       print(f"<span class=Title1><b>=== {book} ===</b></span><br>", file=output)
   ```

**Files Modified**:
- `xenocrates.py` (~120 lines added)

**Testing**:
- Test all 4 sort modes with `test-data-basic.tsv`
- Verify GSE mode compatibility (course-aware sorting)
- Test edge cases (missing books, non-numeric pages, no categories)
- Document interactions with `--enable-categories`

**Backward Compatibility**: 100% - defaults to current alphabetical

---

### 3.3: Acronym Detection

**Priority**: ⭐ Low
**Complexity**: High
**Timeline**: 2-3 days

**Rationale**: Chicago Manual 16.32 requires cross-references from acronyms to full terms. Manual entry is error-prone; auto-detection improves usability.

**Implementation**:

```bash
# Manual mode (default) - use SeeAlso column explicitly
python xenocrates.py notes.tsv index.html

# Auto mode - detect and generate cross-refs
python xenocrates.py notes.tsv index.html --acronym-detection=auto
```

**Detection logic**:
- If title is all caps (2-6 chars) AND has matching long-form entry
- Auto-generate bidirectional cross-references

**Input example**:
```
Title                         | Description
AES                           | Encryption cipher
Advanced Encryption Standard  | Symmetric cipher
IDS                           | Detection system
[No matching long form]
```

**Auto-generated output**:
```
AES
  {b-SEC401 / p-142}
  Encryption cipher
  See: Advanced Encryption Standard

ADVANCED ENCRYPTION STANDARD
  {b-SEC401 / p-142}
  Symmetric cipher
  See also: AES

IDS
  {b-SEC503 / p-89}
  Detection system
  [No auto-reference - no match found]
```

**Changes Required**:

1. **Add `--acronym-detection` flag**:
   ```python
   parser.add_argument(
       '--acronym-detection',
       choices=['manual', 'auto'],
       default='manual',
       help='Acronym handling: manual (use SeeAlso column) or auto (detect)'
   )
   ```

2. **Add `detect_acronyms()` function**:
   ```python
   def detect_acronyms(index):
       """
       Identify potential acronym/longform pairs.

       Returns: dict mapping acronyms to longform titles
       """
       acronyms = {}
       all_titles = list(index.keys())

       for title in all_titles:
           if is_potential_acronym(title):
               # Search for matching long form
               match = match_acronym_to_longform(title, all_titles)
               if match:
                   acronyms[title] = match

       return acronyms
   ```

3. **Add `is_potential_acronym()` helper**:
   ```python
   def is_potential_acronym(title):
       """Check if title looks like an acronym."""
       # 2-6 uppercase letters
       # May have numbers (AES256)
       # No spaces or lowercase
       return 2 <= len(title) <= 8 and title.isupper() and title.isalnum()
   ```

4. **Add `match_acronym_to_longform()` function**:
   ```python
   def match_acronym_to_longform(acronym, titles):
       """
       Find best matching long-form title for acronym.

       Matching criteria:
       - Acronym matches initials of words in title
       - Allow common words to be skipped (the, and, of, for)
       - Score by confidence

       Returns: matching title or None
       """
       candidates = []

       for title in titles:
           if title == acronym:
               continue  # Skip self

           # Extract initials from title
           words = title.split()
           initials = ''.join(w[0] for w in words if w not in SKIP_WORDS)

           # Check match
           if initials == acronym:
               candidates.append((title, 1.0))  # Perfect match
           elif acronym in initials:
               score = len(acronym) / len(initials)
               candidates.append((title, score))

       # Return best match if confidence > 0.8
       if candidates:
           best = max(candidates, key=lambda x: x[1])
           if best[1] > 0.8:
               return best[0]

       return None
   ```

5. **Auto-populate SeeAlso fields**:
   ```python
   if acronym_detection == 'auto':
       acronym_map = detect_acronyms(index)

       # Add bidirectional cross-references
       for acronym, longform in acronym_map.items():
           # Add longform to acronym's SeeAlso
           for ref in index[acronym]:
               if 'seealso' not in ref:
                   ref['seealso'] = []
               ref['seealso'].append(longform)

           # Add acronym to longform's SeeAlso
           for ref in index[longform]:
               if 'seealso' not in ref:
                   ref['seealso'] = []
               ref['seealso'].append(acronym)
   ```

**Files Modified**:
- `xenocrates.py` (~150 lines added)

**Testing**:
- Create `tests/test-acronyms.tsv` with common security acronyms
- Test true positives (AES ↔ Advanced Encryption Standard)
- Test false positives (IDS vs I.D.S., IDS vs "Intrusion Detection System")
- Test edge cases (no match, multiple matches, ambiguous)
- Measure accuracy (target: >90% true positive, <5% false positive)

**Backward Compatibility**: 100% - requires opt-in flag

**Risk Mitigation**:
- Log all auto-detected pairs to stderr for user review
- Provide confidence scores
- Consider whitelist/blacklist config file

---

## Testing Strategy

### Regression Test Suite

**Script**: `tests/run_regression.sh`

```bash
#!/bin/bash
echo "=== Xenocrates Regression Tests ==="

# Test 1: Basic functionality unchanged
python xenocrates.py tests/test-data-basic.tsv /tmp/output1.html
diff /tmp/output1.html tests/expected-output-v2.1.html || echo "FAIL: Basic output"

# Test 2: Compact format
python xenocrates.py tests/test-data-basic.tsv /tmp/output2.html --format=compact
grep -q "font-size:36.0pt" /tmp/output2.html && echo "PASS: Compact format" || echo "FAIL"

# Test 3: Page ranges
python xenocrates.py tests/test-page-ranges.tsv /tmp/output3.html
grep -q "142–147" /tmp/output3.html && echo "PASS: Page ranges" || echo "FAIL"

# Test 4: Grouping
python xenocrates.py tests/test-grouping.tsv /tmp/output4.html
count=$(grep -c "FIREWALL" /tmp/output4.html | head -1)
[ "$count" -eq 1 ] && echo "PASS: Grouping" || echo "FAIL: Found $count entries"

# Test 5-9: Additional features...

echo "=== Tests Complete ==="
```

### Performance Benchmarks

**Script**: `tests/benchmark.sh`

```bash
#!/bin/bash

# Generate large test file (10,000 entries)
python tests/generate_large_dataset.py 10000 > /tmp/large.tsv

# Benchmark v2.0 baseline (if available)
time python archive/xenocrates-v2.0.py /tmp/large.tsv > /dev/null

# Benchmark v2.3 with all features
time python xenocrates.py /tmp/large.tsv /tmp/out.html \
  --format=compact \
  --merge-duplicates \
  --sort-by=title \
  --acronym-detection=auto

# Acceptable: <2x slowdown vs baseline
```

### Word Rendering Validation

**Manual checklist** (`tests/WORD_RENDERING_CHECKLIST.md`):
1. Copy HTML output to clipboard
2. Paste into Microsoft Word
3. Verify:
   - [ ] Section headers render correctly (Aa, Bb, Cc)
   - [ ] Blue titles are blue
   - [ ] Italic cross-references are italic
   - [ ] Bold primary pages are bold
   - [ ] En-dashes in page ranges render correctly
   - [ ] Two-column layout applies cleanly
   - [ ] No HTML tags visible
4. Repeat in Google Docs
5. Test print preview

---

## Release Strategy

### Version Progression

| Version | Features | Release Date | Audience |
|---------|----------|--------------|----------|
| **v2.1-alpha** | 1.1, 1.2 | End of Day 3 | Internal testing |
| **v2.1-beta** | 1.1, 1.2, 1.3 | End of Day 5 | Trusted users |
| **v2.1.0** | All Phase 1 | End of Week 1 | General availability |
| **v2.2-beta** | All Phase 2 | End of Day 12 | Advanced users |
| **v2.2.0** | All Phase 2 | End of Week 2 | General availability |
| **v2.3-beta** | All Phase 3 | End of Day 17 | Power users |
| **v2.3.0** | All Phase 3 | End of Week 3 | General availability |

### Release Checklist

**For each release**:
- [ ] All regression tests passing
- [ ] Performance benchmarks acceptable (<2x baseline)
- [ ] Word rendering validated (Word + Google Docs)
- [ ] README.md updated with new features
- [ ] CHANGELOG.md entry created
- [ ] Example files added to `tests/`
- [ ] Migration notes documented (if breaking changes)
- [ ] Git tag created: `git tag -a v2.1.0 -m "Release v2.1.0"`

---

## Documentation Updates

### Files to Update

1. **README.md** - User-facing documentation
   - Add "New in v2.1/2.2/2.3" sections
   - Update Quick Start examples
   - Add flag documentation
   - Update column table with optional columns

2. **docs/INDEX-STANDARDS.md** (NEW)
   - Document ISO 999 compliance
   - Document Chicago Manual compliance
   - Explain when to use each feature
   - Index creation best practices

3. **docs/MIGRATION-GUIDE.md** (NEW)
   - v2.0 → v2.1 migration
   - v2.1 → v2.2 migration
   - v2.2 → v2.3 migration
   - Troubleshooting

4. **tests/README.md**
   - Document new test files
   - Visual comparison gallery
   - Test execution instructions

5. **CHANGELOG.md** (NEW)
   - Detailed version history
   - Breaking changes highlighted
   - Migration notes

---

## Risk Assessment & Mitigation

### High-Risk Areas

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Phase 1.3 data structure change** | High | Comprehensive unit tests; `--no-grouping` escape hatch |
| **Phase 2.3 category rendering in Word** | Medium | Test in multiple Word versions; clear documentation |
| **Phase 3.3 acronym false positives** | Medium | Default to manual mode; confidence scoring; user review logging |
| **Performance with 10K+ rows** | Medium | Benchmark large files; optimize hotspots; `--fast` mode if needed |

### Rollback Plan

**If major issues discovered post-release**:
1. Revert to previous version tag: `git revert v2.1.0`
2. Document issue in GitHub Issues
3. Release hotfix version (e.g., v2.0.1)
4. Communicate to users via README notice

---

## Success Metrics

### Phase 1 Success Criteria
- ✅ Compact mode reduces output by 20-30%
- ✅ Page ranges parse correctly (100% test cases)
- ✅ Grouping reduces duplicate headers by 80%+
- ✅ Zero regression in existing functionality
- ✅ Performance impact <10% for typical files

### Phase 2 Success Criteria
- ✅ Cross-references render correctly in Word/Docs
- ✅ Primary bolding visible in all targets
- ✅ Category hierarchy renders with proper indentation
- ✅ Optional columns fully backward compatible

### Phase 3 Success Criteria
- ✅ Duplicate merging reduces entries by 5-10%
- ✅ Alternative sorts produce correct output
- ✅ Acronym detection >90% accuracy
- ✅ Performance acceptable with 10K rows (<10s)

---

## Next Steps

### Immediate Actions (This Week)

1. **Review and approve this plan**
2. **Set up development environment**:
   ```bash
   # Create feature branch (already done)
   git checkout claude/review-output-formatting-89bgT

   # Install dev dependencies
   pip install -r requirements-dev.txt  # Create if needed
   ```

3. **Begin Phase 1.1 implementation** (compact mode)
4. **Set up test infrastructure**

### Long-Term Considerations

1. **Configuration file support** (v2.4?):
   ```yaml
   # ~/.xenocrates.conf
   format: detailed
   grouping: true
   merge_duplicates: false
   ```

2. **Interactive mode** (v3.0?):
   ```bash
   python xenocrates.py notes.tsv --interactive
   # GUI for selecting features, previewing output
   ```

3. **Web-based index** (v3.0?):
   - Generate searchable HTML with JavaScript
   - Hyperlinked cross-references
   - Collapsible categories

---

## Appendix A: Data Model Evolution

### v2.0 (Current, post Excel/JSON)
```python
index = [
    ['TITLE_UPPER', 'description', 'page', 'book', 'course'],
    ...
]
```

### v2.1 (Phase 1 complete)
```python
index = {
    'TITLE_UPPER': [
        {
            'description': '...',
            'page': '142-147',
            'page_sort': 142,
            'book': 'SEC401',
            'course': 'SEC575'
        }
    ]
}
```

### v2.2 (Phase 2 complete)
```python
index = {
    'TITLE_UPPER': {
        'category': ('CRYPTOGRAPHY', 'SYMMETRIC'),
        'references': [
            {
                'description': '...',
                'page': '142-147',
                'page_sort': 142,
                'book': 'SEC401',
                'course': 'SEC575',
                'primary': True,
                'seealso': ['AES', 'RSA']
            }
        ]
    }
}
```

### v2.3 (Phase 3 complete)
```python
index = {
    'TITLE_UPPER': {
        'category': ('CRYPTOGRAPHY', 'SYMMETRIC'),
        'is_acronym': False,
        'longform_ref': None,
        'references': [...]
    }
}
```

---

## Appendix B: Command-Line Reference

### All Flags (v2.3)

```bash
python xenocrates.py INPUT OUTPUT [OPTIONS]

Positional arguments:
  INPUT                 Input file (CSV/TSV/Excel/JSON)
  OUTPUT                Output HTML file (or omit for stdout)

Optional arguments:
  -h, --help            Show help message
  --version             Show version number

  # Phase 1 flags
  --format {compact|detailed}
                        Output format (default: detailed)
  --no-grouping         Disable grouping (legacy behavior)

  # Phase 3 flags
  --merge-duplicates    Auto-merge duplicate entries
  --sort-by {title|book|page|category}
                        Sort order (default: title)
  --acronym-detection {manual|auto}
                        Acronym handling (default: manual)

  # Phase 2 flags (feature gates, optional)
  --enable-categories   Enable hierarchical categories
```

### Example Usage

```bash
# Basic usage (v2.0 compatible)
python xenocrates.py notes.tsv index.html

# Compact exam quick-reference (v2.1+)
python xenocrates.py notes.xlsx index.html --format=compact

# Full feature set (v2.3+)
python xenocrates.py notes.xlsx index.html \
  --format=compact \
  --merge-duplicates \
  --sort-by=title \
  --acronym-detection=auto \
  --enable-categories
```

---

## Appendix C: Sample Output Comparison

### Before (v2.0)
```html
<span class=Title1><b><span style='font-size:45.0pt'>Ff</span></b></span>
<span style='font-size:13.5pt'><br><br></span>

<span class=topic><b><span style='color:blue'> FIREWALL </span></b></span>
<span style='color:black'>&nbsp;
<br><i>{b-SEC401 / p-142}</i><br>Packet filtering device<br></span>

<span class=topic><b><span style='color:blue'> FIREWALL </span></b></span>
<span style='color:black'>&nbsp;
<br><i>{b-SEC503 / p-89}</i><br>Network security appliance<br></span>
```

### After (v2.3, all features)
```html
<span class=Title1><b><span style='font-size:36.0pt'>Ff</span></b></span>
<span style='font-size:13.5pt'><br></span>

<span class=topic><b><span style='color:blue'> FIREWALL </span></b></span>
<span style='color:black'>
  <br><i>{b-SEC401 / p-<b>142-147</b>}</i><br>Packet filtering device
  <br><i>See also: IDS, IPS, ACL</i>
  <br><i>{b-SEC503 / p-89}</i><br>Network security appliance<br>
</span>
```

**Key improvements**:
- ✅ Compact font (36pt vs 45pt)
- ✅ Reduced spacing
- ✅ Grouped references (one FIREWALL header)
- ✅ Page ranges (142-147)
- ✅ Bold primary reference
- ✅ Cross-references

---

## End of Implementation Plan

**Questions? Issues?**
Contact: GitHub Issues at bioless/Xenocrates

**Last Updated**: 2026-01-13
**Plan Version**: 1.0
