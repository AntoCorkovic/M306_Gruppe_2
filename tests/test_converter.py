import sys
import os
import pytest
from datetime import datetime
from io import BytesIO
import json
import csv
from src.models.counterstands import Counterstands, TimePeriod, ValueRow
from src.converter import Converter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_counterstands():
    return [
        Counterstands(
            created=datetime(2023, 1, 1),
            timePeriods=[
                TimePeriod(
                    end=datetime(2023, 1, 1, 1, 0),
                    valueRows=[
                        ValueRow(obis="1-1:1.8.1", value=100.0, status="A", valueTimeStamp="2023-01-01T01:00:00"),
                        ValueRow(obis="1-1:2.8.1", value=50.0, status="A", valueTimeStamp="2023-01-01T01:00:00"),
                    ]
                ),
                TimePeriod(
                    end=datetime(2023, 1, 1, 2, 0),
                    valueRows=[
                        ValueRow(obis="1-1:1.8.2", value=110.0, status="A", valueTimeStamp="2023-01-01T02:00:00"),
                        ValueRow(obis="1-1:2.8.2", value=55.0, status="A", valueTimeStamp="2023-01-01T02:00:00"),
                    ]
                )
            ]
        )
    ]


@pytest.fixture
def converter():
    return Converter()


def test_converter_initialization(converter):
    assert converter.sensor_ids == ["ID742", "ID735"]


def test_prepare_data(converter, sample_counterstands):
    data = converter._prepare_data(sample_counterstands)

    assert "ID742" in data
    assert "ID735" in data

    assert len(data["ID742"]) == 2
    assert len(data["ID735"]) == 2

    for sensor_data in data.values():
        for entry in sensor_data:
            assert "ts" in entry
            assert "value" in entry
            assert isinstance(entry["ts"], int)
            assert isinstance(entry["value"], float)


def test_export_to_json(converter, sample_counterstands):
    file = BytesIO()
    converter.export_to_json(sample_counterstands, file)
    file.seek(0)

    json_data = json.loads(file.getvalue().decode('utf-8'))

    assert len(json_data) == 2
    assert json_data[0]["sensorId"] in ["ID742", "ID735"]
    assert json_data[1]["sensorId"] in ["ID742", "ID735"]
    assert json_data[0]["sensorId"] != json_data[1]["sensorId"]

    for sensor_data in json_data:
        assert len(sensor_data["data"]) == 2
        for entry in sensor_data["data"]:
            assert "ts" in entry
            assert "value" in entry


def test_export_to_csv_id742(converter, sample_counterstands):
    file = BytesIO()
    converter.export_to_csv(sample_counterstands, file, "ID742")
    file.seek(0)

    csv_reader = csv.reader(file.getvalue().decode('utf-8').splitlines())
    rows = list(csv_reader)

    assert len(rows) == 3  # Header + 2 data rows
    assert rows[0] == ["timestamp", "value"]
    assert len(rows[1]) == 2
    assert len(rows[2]) == 2


def test_export_to_csv_id735(converter, sample_counterstands):
    file = BytesIO()
    converter.export_to_csv(sample_counterstands, file, "ID735")
    file.seek(0)

    csv_reader = csv.reader(file.getvalue().decode('utf-8').splitlines())
    rows = list(csv_reader)

    assert len(rows) == 3  # Header + 2 data rows
    assert rows[0] == ["timestamp", "value"]
    assert len(rows[1]) == 2
    assert len(rows[2]) == 2


def test_export_to_csv_invalid_sensor_id(converter, sample_counterstands):
    file = BytesIO()
    with pytest.raises(KeyError):
        converter.export_to_csv(sample_counterstands, file, "InvalidID")


def test_prepare_data_empty_counterstands(converter):
    data = converter._prepare_data([])
    assert "ID742" in data
    assert "ID735" in data
    assert len(data["ID742"]) == 0
    assert len(data["ID735"]) == 0


def test_export_to_json_empty_counterstands(converter):
    file = BytesIO()
    converter.export_to_json([], file)
    file.seek(0)

    json_data = json.loads(file.getvalue().decode('utf-8'))
    assert len(json_data) == 2
    assert json_data[0]["data"] == []
    assert json_data[1]["data"] == []


def test_export_to_csv_empty_counterstands(converter):
    file = BytesIO()
    converter.export_to_csv([], file, "ID742")
    file.seek(0)

    csv_reader = csv.reader(file.getvalue().decode('utf-8').splitlines())
    rows = list(csv_reader)
    assert len(rows) == 1  # Only header
    assert rows[0] == ["timestamp", "value"]
