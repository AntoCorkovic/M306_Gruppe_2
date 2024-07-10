import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.parser import Parser


@pytest.fixture(scope="module")
def parsed_data():
    parser = Parser()
    return {
        "counterstands": parser.parse_counterstands(),
        "consumption_values": parser.parse_consumptionvalues()
    }


def test_counterstands_presence(parsed_data):
    # Test if counterstands are present after parsing
    counterstands = parsed_data["counterstands"]
    assert len(counterstands) > 0


def test_counterstands_time_periods(parsed_data):
    # Test if counterstands contain time periods after parsing
    counterstands = parsed_data["counterstands"]
    for item in counterstands:
        assert len(item.timePeriods) > 0


def test_counterstands_values(parsed_data):
    # Test if counterstands values are valid after parsing
    counterstands = parsed_data["counterstands"]
    for item in counterstands:
        for time_period in item.timePeriods:
            for value_row in time_period.valueRows:
                assert isinstance(value_row.value, float)
                assert value_row.value >= 0


def test_consumptionvalues_presence(parsed_data):
    # Test if consumption values are present after parsing
    inflow_and_outflow = parsed_data["consumption_values"]
    assert len(inflow_and_outflow.Inflows) > 0
    assert len(inflow_and_outflow.Outflows) > 0


def test_consumptionvalues_observations(parsed_data):
    # Test if consumption values contain observations after parsing
    inflow_and_outflow = parsed_data["consumption_values"]
    for consumption_type in [inflow_and_outflow.Inflows, inflow_and_outflow.Outflows]:
        for consumption_value in consumption_type:
            assert len(consumption_value.Observations) > 0


def test_consumptionvalues_validity(parsed_data):
    # Test if consumption values' observations are valid after parsing
    inflow_and_outflow = parsed_data["consumption_values"]
    for consumption_type in [inflow_and_outflow.Inflows, inflow_and_outflow.Outflows]:
        for consumption_value in consumption_type:
            for observation in consumption_value.Observations:
                assert isinstance(observation.Sequence, int)
                assert isinstance(observation.Volume, float)
                assert observation.Volume >= 0
