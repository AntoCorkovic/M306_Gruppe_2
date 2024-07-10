import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from io import BytesIO
from datetime import datetime
from src.app import app
from src.parser import Parser
from src.models.counterstands import Counterstands, TimePeriod, ValueRow
from src.models.consumptionvalues import Consumptionvalues, Observation, InflowAndOutflow


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_parser(monkeypatch):
    class MockParser:
        def parse_counterstands(self):
            return [
                Counterstands(
                    created=datetime(2023, 1, 1),
                    timePeriods=[
                        TimePeriod(
                            end=datetime(2023, 1, 1, 1, 0),
                            valueRows=[
                                ValueRow(obis="1-1:1.8.1", value=100.0, status="A",
                                         valueTimeStamp="2023-01-01T01:00:00"),
                                ValueRow(obis="1-1:2.8.1", value=50.0, status="A",
                                         valueTimeStamp="2023-01-01T01:00:00"),
                            ]
                        )
                    ]
                )
            ]

        def parse_consumptionvalues(self):
            return InflowAndOutflow(
                Inflows=[
                    Consumptionvalues(
                        DocumentID=("ID742_20230101",),
                        Observations=[Observation(Sequence=1, Volume=10.0)],
                        StartDateTime=datetime(2023, 1, 1),
                        EndDateTime=datetime(2023, 1, 1, 1, 0),
                        Resolution=15,
                        Unit="kWh"
                    )
                ],
                Outflows=[
                    Consumptionvalues(
                        DocumentID=("ID735_20230101",),
                        Observations=[Observation(Sequence=1, Volume=5.0)],
                        StartDateTime=datetime(2023, 1, 1),
                        EndDateTime=datetime(2023, 1, 1, 1, 0),
                        Resolution=15,
                        Unit="kWh"
                    )
                ]
            )

        def get_observations_for_specific_duration(self, start, end, flows):
            return [Observation(Sequence=1, Volume=10.0)]

        def get_counter_stand(self, start, counterstands, flows, obis):
            return 100.0

    monkeypatch.setattr(Parser, '__new__', lambda cls: MockParser())


def test_download_all_csv(client):
    response = client.get('/download/csv/all')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/zip'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=all_sensor_data.zip')


def test_download_all_json(client):
    response = client.get('/download/json/all')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.headers['Content-Disposition'].startswith('attachment; filename=all_sensor_data.json')


def test_chart(client):
    response = client.get('/chart')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data


def test_chart_data(client, mock_parser):
    response = client.get('/chart/data?startdatetime=01-01-2023 00:00&enddatetime=01-01-2023 01:00')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'inflowData' in data
    assert 'outflowData' in data
    assert 'timeLabels' in data
    assert 'counterstandOfInflowAtStart' in data
    assert 'counterstandOfOutflowAtStart' in data



def test_upload_chart_data_no_files(client):
    response = client.post('/uploadchartdata', data={}, content_type='multipart/form-data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['error'] == 'No file part'


def test_upload_chart_data_missing_file_type(client):
    data = {
        'files': [
            (BytesIO(b'<xml>ESL content</xml>'), 'test_esl.xml'),
        ]
    }
    response = client.post('/uploadchartdata', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['error'] == 'Please upload at least one ESL file and one SDAT file.'
