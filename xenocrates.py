#!/usr/bin/env python3
"""
Xenocrates - GIAC Certification Exam Index Generator

Processes tab-delimited study notes and generates an alphabetically sorted
HTML index for easy reference during GIAC certification exams.

Usage:
    python xenocrates.py <input_file.tsv> > index.html
"""

import sys
import csv
import html
import string
from operator import itemgetter


def read_index_data(filename):
    """
    Read and parse tab-delimited file into index entries.

    Args:
        filename: Path to TSV file with columns: Title, Book, Page, Description

    Returns:
        List of [title_upper, book, page, description] entries

    Raises:
        FileNotFoundError: If input file doesn't exist
        csv.Error: If CSV parsing fails
    """
    index = []

    # Use newline='' for cross-platform CSV compatibility (Mac/Windows/Linux)
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
            try:
                # Validate required columns exist
                title = row.get('Title', '').strip()
                book = row.get('Book', '').strip()
                page = row.get('Page', '').strip()
                description = row.get('Description', '').strip()

                # Skip entries with empty titles
                if not title:
                    continue

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
    Print a single index entry in HTML format.

    Args:
        title: Entry title (will be HTML escaped)
        book: Book/course identifier (will be HTML escaped)
        page: Page number (will be HTML escaped)
        description: Entry description (will be HTML escaped)
    """
    # HTML escape all fields, including quotes (quote=True)
    title_escaped = html.escape(title, quote=True)
    book_escaped = html.escape(book, quote=True)
    page_escaped = html.escape(page, quote=True)
    desc_escaped = html.escape(description, quote=True)

    # Print entry in original format
    print(f"<span class=topic><b><span style='color:blue'>")
    print(f" {title_escaped} ")
    print("</span></b></span><span style='color:black'>&nbsp;")
    print(f"<br><i>{{b-{book_escaped} / p-{page_escaped}}}</i><br>{desc_escaped}<br></span>")


def generate_index(filename):
    """
    Generate HTML index from tab-delimited file.

    Args:
        filename: Path to input TSV file
    """
    # Read and parse input file
    index = read_index_data(filename)

    if not index:
        print("Warning: No valid entries found in input file", file=sys.stderr)
        return

    # Sort alphabetically by title (case-insensitive, already uppercase)
    index = sorted(index, key=itemgetter(0))

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
            print(section_header)
            current_section = section_num

        # Print the entry
        print_entry(title_upper, book, page, description)


def main():
    """Main entry point."""
    # Validate command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python xenocrates.py <input_file.tsv>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python xenocrates.py notes.tsv > index.html", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    try:
        generate_index(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading '{filename}'", file=sys.stderr)
        sys.exit(1)
    except csv.Error as e:
        print(f"Error: CSV parsing failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
