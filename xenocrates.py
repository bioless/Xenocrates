#!/usr/bin/env python3
"""
Xenocrates - GIAC Certification Exam Index Generator

Processes CSV/TSV study notes and generates an alphabetically sorted
HTML index for easy reference during GIAC certification exams.

Usage:
    python xenocrates.py input_file.tsv output_file.html
    python xenocrates.py input_file.csv output_file.html
    python xenocrates.py input_file.tsv > output.html  (legacy mode)

The script automatically detects tab or comma delimiters.
"""

import sys
import csv
import html
import string
import argparse
from operator import itemgetter
from collections import defaultdict

__version__ = "2.0.0"


def detect_delimiter(filename):
    """
    Auto-detect the delimiter (tab or comma) used in the CSV file.

    Args:
        filename: Path to CSV file

    Returns:
        Detected delimiter character ('\t' or ',')
    """
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        # Read first line to detect delimiter
        first_line = f.readline()

        # Count tabs and commas
        tab_count = first_line.count('\t')
        comma_count = first_line.count(',')

        # Prefer tabs (TSV) over commas (CSV)
        if tab_count >= comma_count and tab_count > 0:
            return '\t'
        elif comma_count > 0:
            print("Info: Detected comma-delimited file (CSV)", file=sys.stderr)
            return ','
        else:
            # Default to tab if unclear
            print("Warning: Could not detect delimiter, defaulting to tab", file=sys.stderr)
            return '\t'


def validate_columns(fieldnames):
    """
    Validate that required columns are present in the CSV file.

    Args:
        fieldnames: List of column names from CSV header

    Returns:
        Tuple of (is_valid, missing_columns)
    """
    required_columns = {'Title', 'Book', 'Page', 'Description'}

    if not fieldnames:
        return False, required_columns

    # Convert to set for comparison (handle case variations)
    present_columns = set(fieldnames)
    missing_columns = required_columns - present_columns

    return len(missing_columns) == 0, missing_columns


def read_index_data(filename):
    """
    Read and parse CSV/TSV file into index entries.

    Args:
        filename: Path to CSV/TSV file with columns: Title, Book, Page, Description

    Returns:
        List of [title_upper, book, page, description] entries

    Raises:
        FileNotFoundError: If input file doesn't exist
        csv.Error: If CSV parsing fails
        ValueError: If required columns are missing
    """
    index = []
    empty_title_count = 0
    duplicate_tracker = defaultdict(list)

    # Auto-detect delimiter
    delimiter = detect_delimiter(filename)

    # Use newline='' for cross-platform CSV compatibility (Mac/Windows/Linux)
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=delimiter)

        # Validate required columns are present
        if reader.fieldnames:
            is_valid, missing = validate_columns(reader.fieldnames)
            if not is_valid:
                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}\n"
                    f"Found columns: {', '.join(reader.fieldnames)}\n"
                    f"Required: Title, Book, Page, Description"
                )

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
            try:
                # Validate required columns exist
                title = row.get('Title', '').strip()
                book = row.get('Book', '').strip()
                page = row.get('Page', '').strip()
                description = row.get('Description', '').strip()

                # Skip entries with empty titles but warn user
                if not title:
                    empty_title_count += 1
                    continue

                # Track duplicates (same title, book, page)
                dup_key = (title.upper(), book, page)
                duplicate_tracker[dup_key].append(row_num)

                # Store with uppercase title for sorting, original values for display
                index.append([
                    title.upper(),  # For case-insensitive sorting
                    book,
                    page,
                    description
                ])

            except KeyError as e:
                # Handle missing column
                print(f"Warning: Missing column {e} in row {row_num}, skipping", file=sys.stderr)
                continue
            except Exception as e:
                # Handle other parsing errors
                print(f"Warning: Error parsing row {row_num}: {e}, skipping", file=sys.stderr)
                continue

    # Report statistics
    if empty_title_count > 0:
        print(f"Info: Skipped {empty_title_count} entries with empty titles", file=sys.stderr)

    # Report duplicates
    duplicates = {k: v for k, v in duplicate_tracker.items() if len(v) > 1}
    if duplicates:
        print(f"Warning: Found {len(duplicates)} duplicate entries (same title/book/page):", file=sys.stderr)
        for (title, book, page), rows in list(duplicates.items())[:5]:  # Show first 5
            print(f"  - '{title}' (Book: {book}, Page: {page}) on rows: {', '.join(map(str, rows))}", file=sys.stderr)
        if len(duplicates) > 5:
            print(f"  ... and {len(duplicates) - 5} more duplicates", file=sys.stderr)

    return index


def get_section_header(character):
    """
    Get the HTML section header for a given starting character.

    Args:
        character: First character of the entry title (uppercase)

    Returns:
        Tuple of (section_number, header_html)
    """
    # Map A-Z to section numbers 1-26
    if character in string.ascii_uppercase:
        section_num = ord(character) - ord('A') + 1
        header_label = f"{character}{character.lower()}"
    else:
        # Numbers and special characters
        section_num = 27
        header_label = "Numbers & Special Characters"

    header_html = (
        f"<span class=Title1><b><span style='font-size:45.0pt;line-height:107%;"
        f"color:black'>{header_label}</span></b></span>"
        f"<span style='font-size:13.5pt;line-height:107%;color:black'><br><br></span>"
    )

    return section_num, header_html


def print_entry(title, book, page, description):
    """
    Print a single index entry in HTML format to stdout.

    Args:
        title: Entry title (will be HTML escaped)
        book: Book/course identifier (will be HTML escaped)
        page: Page number (will be HTML escaped)
        description: Entry description (will be HTML escaped)
    """
    print_entry_to_file(title, book, page, description, sys.stdout)


def print_entry_to_file(title, book, page, description, output):
    """
    Print a single index entry in HTML format to specified file.

    Args:
        title: Entry title (will be HTML escaped)
        book: Book/course identifier (will be HTML escaped)
        page: Page number (will be HTML escaped)
        description: Entry description (will be HTML escaped)
        output: File object to write to
    """
    # HTML escape all fields, including quotes (quote=True)
    title_escaped = html.escape(title, quote=True)
    book_escaped = html.escape(book, quote=True)
    page_escaped = html.escape(page, quote=True)
    desc_escaped = html.escape(description, quote=True)

    # Print entry in original format
    print(f"<span class=topic><b><span style='color:blue'>", file=output)
    print(f" {title_escaped} ", file=output)
    print("</span></b></span><span style='color:black'>&nbsp;", file=output)
    print(f"<br><i>{{b-{book_escaped} / p-{page_escaped}}}</i><br>{desc_escaped}<br></span>", file=output)


def generate_index(filename, output_file=None):
    """
    Generate HTML index from CSV/TSV file.

    Args:
        filename: Path to input CSV/TSV file
        output_file: Optional path to output HTML file (default: stdout)
    """
    # Read and parse input file
    index = read_index_data(filename)

    if not index:
        print("Warning: No valid entries found in input file", file=sys.stderr)
        return

    # Sort alphabetically by title (case-insensitive, already uppercase)
    index = sorted(index, key=itemgetter(0))

    # Redirect output to file if specified
    output = open(output_file, 'w', encoding='utf-8') if output_file else sys.stdout

    try:
        # Track current section to avoid duplicate headers
        current_section = 0

        # Process each entry
        for entry in index:
            title_upper, book, page, description = entry

            # Get first character (strip quotes if present)
            first_char = title_upper.strip('"').lstrip('"')[0] if title_upper else ''

            if not first_char:
                continue

            # Determine section and print header if changed
            section_num, section_header = get_section_header(first_char)

            if section_num != current_section:
                print(section_header, file=output)
                current_section = section_num

            # Print the entry with explicit file parameter
            print_entry_to_file(title_upper, book, page, description, output)

        if output_file:
            print(f"Success: Generated index with {len(index)} entries → {output_file}", file=sys.stderr)

    finally:
        if output_file and output != sys.stdout:
            output.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Xenocrates - GIAC Certification Exam Index Generator',
        epilog='Example: xenocrates.py notes.tsv index.html'
    )

    parser.add_argument(
        'input_file',
        help='Input CSV/TSV file with columns: Title, Book, Page, Description'
    )

    parser.add_argument(
        'output_file',
        nargs='?',
        default=None,
        help='Output HTML file (default: print to stdout for redirection)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'Xenocrates {__version__}'
    )

    args = parser.parse_args()

    try:
        generate_index(args.input_file, args.output_file)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading '{args.input_file}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except csv.Error as e:
        print(f"Error: CSV parsing failed: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"Error: File encoding issue: {e}", file=sys.stderr)
        print("Tip: Ensure file is saved as UTF-8", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
