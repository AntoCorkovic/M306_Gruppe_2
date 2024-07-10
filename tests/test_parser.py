import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from parser import Parser
from models.counterstands import Counterstands, TimePeriod, ValueRow
from models.consumptionvalues import Consumptionvalues, Observation
import xml.etree.ElementTree as ET


@pytest.fixture
def parser():
    return Parser()


def create_mock_esl_tree():
    root = ET.Element("ESLBillingData")
    header = ET.SubElement(root, "Header", version="1.0", created="2019-01-31T00:00:00", swSystemNameFrom="ESL-EVU",
                           swSystemNameTo="ESL-EVU")
    meter = ET.SubElement(root, "Meter", factoryNo="38157930", internalNo="38157930")
    time_period = ET.SubElement(meter, "TimePeriod", end="2019-01-01T00:00:00")
    ET.SubElement(time_period, "ValueRow", obis="1-1:1.8.1", value="4755.3000", status="V")
    ET.SubElement(time_period, "ValueRow", obis="1-1:1.8.2", value="14460.9000", status="V")
    ET.SubElement(time_period, "ValueRow", obis="1-1:2.8.1", value="8258.1000", status="V")
    ET.SubElement(time_period, "ValueRow", obis="1-1:2.8.2", value="3543.1000", status="V")
    return ET.ElementTree(root)


def create_mock_sdat_tree():
    ns = {'rsm': 'http://www.strom.ch'}
    root = ET.Element("{http://www.strom.ch}ValidatedMeteredData_12")
    header = ET.SubElement(root, "{http://www.strom.ch}ValidatedMeteredData_HeaderInformation")
    instance_doc = ET.SubElement(header, "{http://www.strom.ch}InstanceDocument")
    ET.SubElement(instance_doc, "{http://www.strom.ch}DocumentID").text = "eslevu121963_BR2294_ID742"
    metering_data = ET.SubElement(root, "{http://www.strom.ch}MeteringData")
    ET.SubElement(metering_data, "{http://www.strom.ch}DocumentID").text = "eslevu121963_D"
    interval = ET.SubElement(metering_data, "{http://www.strom.ch}Interval")
    ET.SubElement(interval, "{http://www.strom.ch}StartDateTime").text = "2019-03-11T23:00:00Z"
    ET.SubElement(interval, "{http://www.strom.ch}EndDateTime").text = "2019-03-12T23:00:00Z"
    resolution = ET.SubElement(metering_data, "{http://www.strom.ch}Resolution")
    ET.SubElement(resolution, "{http://www.strom.ch}Resolution").text = "15"
    ET.SubElement(resolution, "{http://www.strom.ch}Unit").text = "MIN"
    for i in range(1, 97):
        observation = ET.SubElement(metering_data, "{http://www.strom.ch}Observation")
        position = ET.SubElement(observation, "{http://www.strom.ch}Position")
        ET.SubElement(position, "{http://www.strom.ch}Sequence").text = str(i)
        ET.SubElement(observation, "{http://www.strom.ch}Volume").text = f"{i * 0.1:.3f}"
    return ET.ElementTree(root)


def test_parse_counterstands(parser):
    with patch('os.listdir', return_value=['test_file.xml']):
        with patch('xml.etree.ElementTree.parse', return_value=create_mock_esl_tree()):
            counterstands = parser.parse_counterstands()

    assert len(counterstands) == 1
    assert isinstance(counterstands[0], Counterstands)
    assert len(counterstands[0].timePeriods) == 1
    assert len(counterstands[0].timePeriods[0].valueRows) == 4  # We have 4 ValueRows in our mock data


def test_parse_consumptionvalues(parser):
    with patch('os.listdir', return_value=['test_file.xml']):
        with patch('xml.etree.ElementTree.parse', return_value=create_mock_sdat_tree()):
            inflow_and_outflow = parser.parse_consumptionvalues()

    assert len(inflow_and_outflow.Inflows) == 1
    assert len(inflow_and_outflow.Outflows) == 0
    assert isinstance(inflow_and_outflow.Inflows[0], Consumptionvalues)
    assert inflow_and_outflow.Inflows[0].DocumentID[0] == "eslevu121963_BR2294_ID742"
    assert len(inflow_and_outflow.Inflows[0].Observations) == 96  # We have 96 observations in our mock data


def test_parse_counterstands_for_upload(parser):
    mock_file = MagicMock()
    mock_file.read.return_value = ET.tostring(create_mock_esl_tree().getroot())
    mock_file.filename = "test_file.xml"

    counterstands = parser.parse_counterstands_for_upload([mock_file])

    assert len(counterstands) == 1
    assert isinstance(counterstands[0], Counterstands)
    assert len(counterstands[0].timePeriods) == 1
    assert len(counterstands[0].timePeriods[0].valueRows) == 4  # We have 4 ValueRows in our mock data


def test_parse_consumptionvalues_for_upload(parser):
    mock_file = MagicMock()
    mock_file.read.return_value = ET.tostring(create_mock_sdat_tree().getroot())
    mock_file.filename = "test_file.xml"

    inflow_and_outflow = parser.parse_consumptionvalues_for_upload([mock_file])

    assert len(inflow_and_outflow.Inflows) == 1
    assert len(inflow_and_outflow.Outflows) == 0
    assert isinstance(inflow_and_outflow.Inflows[0], Consumptionvalues)
    assert inflow_and_outflow.Inflows[0].DocumentID[0] == "eslevu121963_BR2294_ID742"
    assert len(inflow_and_outflow.Inflows[0].Observations) == 96  # We have 96 observations in our mock data


def test_get_nearest_older_observation(parser):
    inflows = [
        Consumptionvalues(StartDateTime=datetime(2023, 1, 1, 0, 0)),
        Consumptionvalues(StartDateTime=datetime(2023, 1, 1, 1, 0)),
        Consumptionvalues(StartDateTime=datetime(2023, 1, 1, 2, 0))
    ]
    start = datetime(2023, 1, 1, 1, 30)

    result = parser.get_nearest_older_observation(inflows, start)
    assert result.StartDateTime == datetime(2023, 1, 1, 1, 0)


def test_find_closest_time_period(parser):
    counterstands = [
        Counterstands(
            created=datetime(2023, 1, 1),
            timePeriods=[
                TimePeriod(
                    end=datetime(2023, 1, 1, 1, 0),
                    valueRows=[
                        ValueRow(obis="1-1:1.8.1", value=100.0, status="A", valueTimeStamp="2023-01-01T01:00:00"),
                        ValueRow(obis="1-1:2.8.1", value=50.0, status="A", valueTimeStamp="2023-01-01T01:00:00")
                    ]
                )
            ]
        )
    ]
    end_date = datetime(2023, 1, 1, 1, 30)
    obis = {"1-1:1.8.1", "1-1:2.8.1"}

    result = parser.find_closest_time_period(counterstands, end_date, obis)
    assert result["end"] == datetime(2023, 1, 1, 1, 0)
    assert result["total_value"] == 150.0


def test_get_observations_for_specific_duration(parser):
    flows = [
        Consumptionvalues(
            StartDateTime=datetime(2023, 1, 1, 0, 0),
            EndDateTime=datetime(2023, 1, 1, 1, 0),
            Observations=[
                Observation(Sequence=1, Volume=10.0),
                Observation(Sequence=2, Volume=20.0),
                Observation(Sequence=3, Volume=30.0),
                Observation(Sequence=4, Volume=40.0)
            ]
        )
    ]
    start = datetime(2023, 1, 1, 0, 15)
    end = datetime(2023, 1, 1, 0, 45)

    result = parser.get_observations_for_specific_duration(start, end, flows)
    assert len(result) == 2
    assert result[0].Volume == 20.0
    assert result[1].Volume == 30.0


def test_get_counter_stand(parser):
    counterstands = [
        Counterstands(
            created=datetime(2023, 1, 1),
            timePeriods=[
                TimePeriod(
                    end=datetime(2023, 1, 1, 1, 0),
                    valueRows=[
                        ValueRow(obis="1-1:1.8.1", value=100.0, status="A", valueTimeStamp="2023-01-01T01:00:00"),
                        ValueRow(obis="1-1:2.8.1", value=50.0, status="A", valueTimeStamp="2023-01-01T01:00:00")
                    ]
                )
            ]
        )
    ]
    flows = [
        Consumptionvalues(
            StartDateTime=datetime(2023, 1, 1, 1, 0),
            EndDateTime=datetime(2023, 1, 1, 2, 0),
            Observations=[
                Observation(Sequence=1, Volume=10.0),
                Observation(Sequence=2, Volume=20.0)
            ]
        )
    ]
    start = datetime(2023, 1, 1, 1, 30)
    obis = {"1-1:1.8.1", "1-1:2.8.1"}

    result = parser.get_counter_stand(start, counterstands, flows, obis)
    assert result == 120.0  # 150.0 - 30.0