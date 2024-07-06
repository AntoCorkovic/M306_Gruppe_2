import pytest
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from src.parser import Parser
from src.models.consumptionvalues import Observation


# Create a fixture to set up Flask app and temporary directories
@pytest.fixture
def app():
    app = Flask(__name__)

    # Set up temporary directories
    temp_outflow_dir = tempfile.mkdtemp()
    temp_inflow_dir = tempfile.mkdtemp()

    # Copy test data files into temporary directories
    testdata_dir = os.path.join(os.path.dirname(__file__), 'testdata')
    outflow_files = [f for f in os.listdir(testdata_dir) if f.startswith('ESL-Files')]
    inflow_files = [f for f in os.listdir(testdata_dir) if f.startswith('SDAT-Files')]

    for file in outflow_files:
        shutil.copyfile(os.path.join(testdata_dir, file), os.path.join(temp_outflow_dir, file))

    for file in inflow_files:
        shutil.copyfile(os.path.join(testdata_dir, file), os.path.join(temp_inflow_dir, file))

    # Replace Parser's directories with temporary ones
    parser = Parser()
    parser.OUTFLOW_DIRECTORY = temp_outflow_dir
    parser.INFLOW_DIRECTORY = temp_inflow_dir

    # Define routes and corresponding logic
    @app.route('/chart/data')
    def chart_data():
        startdatetime_str = request.args.get('startdatetime')
        enddatetime_str = request.args.get('enddatetime')
        startdatetime = datetime.strptime(startdatetime_str, '%d-%m-%Y %H:%M')
        enddatetime = datetime.strptime(enddatetime_str, '%d-%m-%Y %H:%M')

        # Example of using Parser methods within Flask route
        inflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                            parser.parse_consumptionvalues().Inflows)
        outflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                             parser.parse_consumptionvalues().Outflows)

        inflow_data = [obs.Volume for obs in inflow_observations]
        outflow_data = [obs.Volume for obs in outflow_observations]
        time_labels = [(startdatetime + timedelta(minutes=15 * i)).strftime('%d-%m-%Y %H:%M') for i in
                       range(len(inflow_data))]

        total_inflow = round(sum(inflow_data), 2)
        total_outflow = round(sum(outflow_data), 2)
        procent_inflow = round(total_inflow / (total_inflow + total_outflow) * 100, 2)
        procent_outflow = round(total_outflow / (total_inflow + total_outflow) * 100, 2)

        data = {
            'inflowData': inflow_data,
            'outflowData': outflow_data,
            'timeLabels': time_labels,
            'totalInflow': total_inflow,
            'totalOutflow': total_outflow,
            'procentInflow': procent_inflow,
            'procentOutflow': procent_outflow,
            "startdatetime": startdatetime,
            "enddatetime": enddatetime,
        }

        return jsonify(data)

    yield app

    # Teardown: Remove temporary directories after tests
    shutil.rmtree(temp_outflow_dir)
    shutil.rmtree(temp_inflow_dir)


def test_chart_data_endpoint(app):
    client = app.test_client()
    response = client.get('/chart/data?startdatetime=01-01-2024 00:00&enddatetime=01-01-2024 01:00')

    assert response.status_code == 200
    data = response.get_json()

    # Add assertions based on expected data in the response
    assert 'inflowData' in data
    assert 'outflowData' in data
    assert 'timeLabels' in data
    assert 'totalInflow' in data
    assert 'totalOutflow' in data
    assert 'procentInflow' in data
    assert 'procentOutflow' in data
    assert 'startdatetime' in data
    assert 'enddatetime' in data
