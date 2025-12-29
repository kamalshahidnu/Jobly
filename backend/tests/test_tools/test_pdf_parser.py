"""Tests for PDF parser tool."""

import pytest
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

    def test_extract_text_returns_string(self, parser):
        """Test extract_text returns string."""
        # TODO: Create test PDF file
        result = parser.extract_text("/path/to/test.pdf")
        assert isinstance(result, str)

    def test_extract_metadata_returns_dict(self, parser):
        """Test extract_metadata returns dictionary."""
        # TODO: Create test PDF file
        result = parser.extract_metadata("/path/to/test.pdf")
        assert isinstance(result, dict)
