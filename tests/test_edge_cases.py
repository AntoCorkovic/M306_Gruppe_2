import pytest
import os
import tempfile
import shutil

from src.parser import Parser

# Test with empty directories or no files to ensure the parser behaves correctly and returns empty lists or objects.


# Fixture to set up temporary directories for testing

OUTFLOW_DIRECTORY = '../testdata/ESL-Files/'
INFLOW_DIRECTORY = '../testdata/SDAT-Files/'


@pytest.fixture(scope="module")
def temp_directories():
    temp_outflow_dir = tempfile.mkdtemp()
    temp_inflow_dir = tempfile.mkdtemp()

    # Copy test data files into temporary directories
    outflow_files = [f for f in os.listdir(OUTFLOW_DIRECTORY)]
    inflow_files = [f for f in os.listdir(INFLOW_DIRECTORY)]

    for file in outflow_files:
        shutil.copyfile(os.path.join(OUTFLOW_DIRECTORY, file), os.path.join(temp_outflow_dir, file))

    for file in inflow_files:
        shutil.copyfile(os.path.join(INFLOW_DIRECTORY, file), os.path.join(temp_inflow_dir, file))

    yield {
        'temp_outflow_dir': temp_outflow_dir,
        'temp_inflow_dir': temp_inflow_dir
    }

    shutil.rmtree(temp_outflow_dir)
    shutil.rmtree(temp_inflow_dir)


# Use temp_directories fixture in your tests
def test_parse_counterstands_empty_directory(temp_directories):
    temp_outflow_dir = temp_directories['temp_outflow_dir']

    parser = Parser()
    parser.OUTFLOW_DIRECTORY = temp_outflow_dir
    counterstands = parser.parse_counterstands()
    assert counterstands == []


def test_parse_consumptionvalues_empty_directory(temp_directories):
    temp_inflow_dir = temp_directories['temp_inflow_dir']

    parser = Parser()
    parser.INFLOW_DIRECTORY = temp_inflow_dir
    inflow_and_outflow = parser.parse_consumptionvalues()
    assert len(inflow_and_outflow.Inflows) == 0
    assert len(inflow_and_outflow.Outflows) == 0
