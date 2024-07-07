import pytest

from src.parser import Parser


# Test scenarios where parsing fails due to invalid XML or other issues. Ensure appropriate exceptions are raised or
# handled gracefully.

def test_parse_counterstands_invalid_xml():
    # Mock or provide a test file with invalid XML structure
    with pytest.raises(Exception):
        parser = Parser()
        parser.parse_counterstands()


def test_parse_consumptionvalues_invalid_xml():
    # Mock or provide a test file with invalid XML structure
    with pytest.raises(Exception):
        parser = Parser()
        parser.parse_consumptionvalues()
