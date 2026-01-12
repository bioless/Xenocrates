#!/usr/bin/env python3
"""
Automated tests for Xenocrates.

Run with: pytest tests/test_xenocrates.py -v
"""

import os
import sys

import pytest

# Add parent directory to path so we can import xenocrates
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import xenocrates  # noqa: E402


class TestFileFormatDetection:
    """Test file format detection from extensions."""

    def test_detect_csv_format(self):
        """Test .csv extension detection."""
        assert xenocrates.detect_file_format("test.csv") == "csv"

    def test_detect_tsv_format(self):
        """Test .tsv extension detection."""
        assert xenocrates.detect_file_format("test.tsv") == "tsv"

    def test_detect_excel_format(self):
        """Test .xlsx extension detection."""
        assert xenocrates.detect_file_format("test.xlsx") == "excel"

    def test_detect_json_format(self):
        """Test .json extension detection."""
        assert xenocrates.detect_file_format("test.json") == "json"

    def test_detect_txt_as_csv(self):
        """Test .txt extension defaults to csv."""
        assert xenocrates.detect_file_format("test.txt") == "csv"

    def test_unsupported_format_raises_error(self):
        """Test unsupported format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            xenocrates.detect_file_format("test.pdf")

    def test_case_insensitive_extensions(self):
        """Test extension detection is case-insensitive."""
        assert xenocrates.detect_file_format("test.CSV") == "csv"
        assert xenocrates.detect_file_format("test.XLSX") == "excel"


class TestColumnValidation:
    """Test column name validation and normalization."""

    def test_valid_columns(self):
        """Test validation with all required columns."""
        fieldnames = ["Title", "Description", "Page", "Book"]
        is_valid, error_msg, column_map = xenocrates.validate_columns(fieldnames)
        assert is_valid is True
        assert error_msg == ""
        assert len(column_map) == 4

    def test_valid_columns_with_course(self):
        """Test validation with optional Course column."""
        fieldnames = ["Title", "Description", "Page", "Book", "Course"]
        is_valid, error_msg, column_map = xenocrates.validate_columns(fieldnames)
        assert is_valid is True
        assert "Course" in column_map

    def test_case_insensitive_columns(self):
        """Test column names are case-insensitive."""
        fieldnames = ["title", "description", "page", "book"]
        is_valid, error_msg, column_map = xenocrates.validate_columns(fieldnames)
        assert is_valid is True

    def test_mixed_case_columns(self):
        """Test mixed case column names."""
        fieldnames = ["TITLE", "Description", "PAGE", "book"]
        is_valid, error_msg, column_map = xenocrates.validate_columns(fieldnames)
        assert is_valid is True

    def test_missing_required_column(self):
        """Test validation fails with missing required column."""
        fieldnames = ["Title", "Page", "Book"]  # Missing Description
        is_valid, error_msg, column_map = xenocrates.validate_columns(fieldnames)
        assert is_valid is False
        assert "Description" in error_msg

    def test_empty_fieldnames(self):
        """Test validation fails with empty fieldnames."""
        is_valid, error_msg, column_map = xenocrates.validate_columns([])
        assert is_valid is False
        assert "No columns found" in error_msg

    def test_column_order_doesnt_matter(self):
        """Test columns can be in any order."""
        fieldnames = ["Book", "Page", "Title", "Description"]  # Different order
        is_valid, error_msg, column_map = xenocrates.validate_columns(fieldnames)
        assert is_valid is True


class TestCSVReading:
    """Test CSV/TSV file reading."""

    def test_read_basic_tsv(self):
        """Test reading basic TSV file."""
        index, has_course = xenocrates.read_csv_data("tests/test-data-basic.tsv")
        assert len(index) == 79
        assert has_course is False
        # Check first entry structure
        assert len(index[0]) == 5  # [title_upper, description, page, book, course]

    def test_read_csv_format(self):
        """Test reading CSV (comma-delimited) file."""
        index, has_course = xenocrates.read_csv_data("tests/test-data-csv.csv")
        assert len(index) >= 1
        assert has_course is False

    def test_read_gse_format(self):
        """Test reading GSE format with Course column."""
        index, has_course = xenocrates.read_csv_data("tests/test-gse-with-course.tsv")
        assert has_course is True
        # Check that course data is present in entries
        for entry in index:
            assert len(entry) == 5

    def test_read_lowercase_columns(self):
        """Test reading file with lowercase column names."""
        index, has_course = xenocrates.read_csv_data("tests/test-lowercase-columns.tsv")
        assert len(index) >= 1
        assert has_course is False


class TestExcelReading:
    """Test Excel file reading."""

    def test_read_basic_excel(self):
        """Test reading basic Excel file."""
        index, has_course = xenocrates.read_excel_data("tests/test-data-excel.xlsx")
        assert len(index) == 10
        assert has_course is False

    def test_read_excel_gse_format(self):
        """Test reading Excel with Course column."""
        index, has_course = xenocrates.read_excel_data("tests/test-data-excel-gse.xlsx")
        assert len(index) == 3
        assert has_course is True

    def test_read_excel_lowercase_columns(self):
        """Test reading Excel with lowercase column names."""
        index, has_course = xenocrates.read_excel_data("tests/test-excel-lowercase-columns.xlsx")
        assert len(index) == 3
        assert has_course is False

    def test_excel_entry_structure(self):
        """Test Excel entries have correct structure."""
        index, _ = xenocrates.read_excel_data("tests/test-data-excel.xlsx")
        first_entry = index[0]
        assert len(first_entry) == 5
        # Check fields are strings
        assert isinstance(first_entry[0], str)  # title_upper
        assert isinstance(first_entry[1], str)  # description
        assert isinstance(first_entry[2], str)  # page
        assert isinstance(first_entry[3], str)  # book
        assert isinstance(first_entry[4], str)  # course (empty string if no course)


class TestJSONReading:
    """Test JSON file reading."""

    def test_read_json_wrapped_format(self):
        """Test reading JSON with wrapped format."""
        index, has_course = xenocrates.read_json_data("tests/test-data.json")
        assert len(index) == 10
        assert has_course is False

    def test_read_json_direct_array(self):
        """Test reading JSON with direct array format."""
        index, has_course = xenocrates.read_json_data("tests/test-data-json-direct.json")
        assert len(index) == 10
        assert has_course is False

    def test_read_json_gse_format(self):
        """Test reading JSON with Course column."""
        index, has_course = xenocrates.read_json_data("tests/test-data-json-gse.json")
        assert len(index) == 3
        assert has_course is True

    def test_json_entry_structure(self):
        """Test JSON entries have correct structure."""
        index, _ = xenocrates.read_json_data("tests/test-data.json")
        first_entry = index[0]
        assert len(first_entry) == 5
        # Check all fields are strings
        for field in first_entry:
            assert isinstance(field, str)


class TestUnifiedReader:
    """Test unified read_input_file() dispatcher."""

    def test_reads_csv_via_dispatcher(self):
        """Test dispatcher correctly routes CSV files."""
        index, has_course = xenocrates.read_input_file("tests/test-data-csv.csv")
        assert len(index) >= 1

    def test_reads_tsv_via_dispatcher(self):
        """Test dispatcher correctly routes TSV files."""
        index, has_course = xenocrates.read_input_file("tests/test-data-basic.tsv")
        assert len(index) == 79

    def test_reads_excel_via_dispatcher(self):
        """Test dispatcher correctly routes Excel files."""
        index, has_course = xenocrates.read_input_file("tests/test-data-excel.xlsx")
        assert len(index) == 10

    def test_reads_json_via_dispatcher(self):
        """Test dispatcher correctly routes JSON files."""
        index, has_course = xenocrates.read_input_file("tests/test-data.json")
        assert len(index) == 10


class TestDataQuality:
    """Test data quality features (duplicates, empty entries, etc.)."""

    def test_alphabetical_sorting(self):
        """Test entries can be sorted alphabetically."""
        index, _ = xenocrates.read_csv_data("tests/test-data-basic.tsv")
        # Get titles (first element of each entry)
        titles = [entry[0] for entry in index]
        # Verify sorting works (Note: read_csv_data doesn't sort, generate_index does)
        sorted_titles = sorted(titles)
        assert len(titles) == len(sorted_titles)
        # Just verify the structure is correct for sorting
        for title in titles:
            assert title == title.upper()  # All should be uppercase

    def test_case_insensitive_sorting(self):
        """Test sorting is case-insensitive (all uppercase)."""
        index, _ = xenocrates.read_csv_data("tests/test-data-basic.tsv")
        # All titles should be uppercase for sorting
        for entry in index:
            title_upper = entry[0]
            assert title_upper == title_upper.upper()


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_file_not_found(self):
        """Test FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            xenocrates.read_csv_data("nonexistent.tsv")

    def test_invalid_json_format(self):
        """Test error handling for invalid JSON."""
        # Create temporary invalid JSON file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json syntax')
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON format"):
                xenocrates.read_json_data(temp_path)
        finally:
            os.unlink(temp_path)

    def test_missing_columns_error(self):
        """Test error message for missing required columns."""
        # Create temporary file with wrong columns
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tsv", delete=False) as f:
            f.write("Title\tBook\tPage\n")  # Missing Description
            f.write("Test\tSEC401\t100\n")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Missing required columns"):
                xenocrates.read_csv_data(temp_path)
        finally:
            os.unlink(temp_path)


class TestSectionHeaders:
    """Test section header generation."""

    def test_letter_section_header(self):
        """Test section header for letters."""
        section_num, header_html = xenocrates.get_section_header("A")
        assert section_num == 1
        assert "Aa" in header_html

        section_num, header_html = xenocrates.get_section_header("Z")
        assert section_num == 26
        assert "Zz" in header_html

    def test_number_section_header(self):
        """Test section header for numbers."""
        section_num, header_html = xenocrates.get_section_header("1")
        assert section_num == 27
        assert "Numbers & Special Characters" in header_html

    def test_special_char_section_header(self):
        """Test section header for special characters."""
        section_num, header_html = xenocrates.get_section_header("@")
        assert section_num == 27
        assert "Numbers & Special Characters" in header_html


class TestIntegration:
    """Integration tests for end-to-end functionality."""

    def test_full_pipeline_csv(self):
        """Test complete pipeline with CSV input."""
        import tempfile

        # Generate index to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_output = f.name

        try:
            xenocrates.generate_index("tests/test-data-basic.tsv", temp_output)

            # Verify output file was created and has content
            assert os.path.exists(temp_output)
            assert os.path.getsize(temp_output) > 0

            # Check HTML content
            with open(temp_output, "r", encoding="utf-8") as f:
                content = f.read()
                # Should contain section headers
                assert "Aa" in content or "Bb" in content
                # Should contain entry formatting
                assert "class=topic" in content
        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)

    def test_full_pipeline_excel(self):
        """Test complete pipeline with Excel input."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_output = f.name

        try:
            xenocrates.generate_index("tests/test-data-excel.xlsx", temp_output)

            assert os.path.exists(temp_output)
            assert os.path.getsize(temp_output) > 0
        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)

    def test_full_pipeline_json(self):
        """Test complete pipeline with JSON input."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_output = f.name

        try:
            xenocrates.generate_index("tests/test-data.json", temp_output)

            assert os.path.exists(temp_output)
            assert os.path.getsize(temp_output) > 0
        finally:
            if os.path.exists(temp_output):
                os.unlink(temp_output)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
