"""Tests for PDF parser tool."""

import pytest
from PyPDF2 import PdfWriter
from jobly.tools.pdf_parser import PDFParser


class TestPDFParser:
    """Test cases for PDFParser."""

    @pytest.fixture
    def parser(self):
        """Create PDFParser instance.

        Returns:
            PDFParser instance
        """
        return PDFParser()

    def test_parser_initialization(self, parser):
        """Test parser initialization."""
        assert parser is not None

    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        """Create a minimal PDF file for parsing tests."""
        out_path = tmp_path / "sample.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)  # US letter points
        writer.add_metadata({"/Title": "Sample"})
        with open(out_path, "wb") as handle:
            writer.write(handle)
        return str(out_path)

    def test_extract_text_returns_string(self, parser, sample_pdf_path):
        """Test extract_text returns string."""
        result = parser.extract_text(sample_pdf_path)
        assert isinstance(result, str)

    def test_extract_metadata_returns_dict(self, parser, sample_pdf_path):
        """Test extract_metadata returns dictionary."""
        result = parser.extract_metadata(sample_pdf_path)
        assert isinstance(result, dict)
