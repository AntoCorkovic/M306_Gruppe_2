import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_file
from io import BytesIO
from converter import Converter
from parser import Parser
import zipfile

app = Flask(__name__)

counterstands = None
consumptionvalues = None


@app.route('/download/csv/all')
def download_all_csv():
    parser = Parser()
    converter = Converter()

    # Parse data for all sensor IDs
    counterstands = parser.parse_counterstands()

    # Create a ZIP file in memory
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for sensor_id in converter.sensor_ids:
            csv_data = BytesIO()
            converter.export_to_csv(counterstands, csv_data, sensor_id)
            csv_data.seek(0)
            zf.writestr(f"{sensor_id}.csv", csv_data.getvalue())

    memory_file.seek(0)
    return send_file(memory_file,
                     mimetype='application/zip',
                     as_attachment=True,
                     download_name='all_sensor_data.zip')


@app.route('/download/json/all')
def download_all_json():
    parser = Parser()
    converter = Converter()

    # Parse data for all sensor IDs
    counterstands = parser.parse_counterstands()

    # Create JSON data for all sensors
    json_data = BytesIO()
    converter.export_to_json(counterstands, json_data)
    json_data.seek(0)

    return send_file(json_data,
                     mimetype='application/json',
                     as_attachment=True,
                     download_name='all_sensor_data.json')


@app.route('/chart')
def chart():
    return render_template('frontend/chart.html')


@app.route('/chart/data')
def chart_data():
    global counterstands, consumptionvalues
    parser = Parser()

    if counterstands is None and consumptionvalues is None:
        counterstands = parser.parse_counterstands()
        consumptionvalues = parser.parse_consumptionvalues()

    startdatetime_str = request.args.get('startdatetime')
    enddatetime_str = request.args.get('enddatetime')

    # Convert the datetime strings to datetime objects
    startdatetime = datetime.strptime(startdatetime_str, '%d-%m-%Y %H:%M')
    enddatetime = datetime.strptime(enddatetime_str, '%d-%m-%Y %H:%M')

    inflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                        consumptionvalues.Inflows)
    outflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                         consumptionvalues.Outflows)
    counterstand_of_inflow_at_start = parser.get_counter_stand(startdatetime, counterstands, consumptionvalues.Inflows,
                                                               {"1-1:1.8.1", "1-1:1.8.2"})
    counterstand_of_outflow_at_start = parser.get_counter_stand(startdatetime, counterstands,
                                                                consumptionvalues.Outflows,
                                                                {"1-1:2.8.1", "1-1:2.8.2"})

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
        'counterstandOfInflowAtStart': counterstand_of_inflow_at_start,
        'counterstandOfOutflowAtStart': counterstand_of_outflow_at_start,
        'totalInflow': total_inflow,
        'totalOutflow': total_outflow,
        'procentInflow': procent_inflow,
        'procentOutflow': procent_outflow,
        "startdatetime": startdatetime,
        "enddatetime": enddatetime,
    }

    return jsonify(data)


@app.route('/uploadchartdata', methods=['POST'])
def upload_chart_data():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'})

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files uploaded'})

    esl_files = []
    sdat_files = []

    for file in files:
        if file and file.filename.endswith('.xml'):
            if 'sdat' in file.filename.lower():
                sdat_files.append(file)
            elif 'esl' in file.filename.lower():
                esl_files.append(file)

    if len(esl_files) == 0 or len(sdat_files) == 0:
        return jsonify({'error': 'Please upload at least one ESL file and one SDAT file.'})

    parser = Parser()

    counterstandsupload = parser.parse_counterstands_for_upload(esl_files)
    consumptionvaluesupload = parser.parse_consumptionvalues_for_upload(sdat_files)

    if counterstandsupload is None or consumptionvaluesupload is None:  # pragma: no cover
        return jsonify({'error': 'Failed to parse uploaded files'})

    startdatetime, enddatetime = find_start_and_end_datetime(consumptionvaluesupload, counterstandsupload)

    if (len(consumptionvaluesupload.Inflows) > 0):
        inflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                            consumptionvaluesupload.Inflows)
        counterstand_of_inflow_at_start = parser.get_counter_stand(startdatetime, counterstandsupload,
                                                                   consumptionvaluesupload.Inflows,
                                                                   {"1-1:1.8.1", "1-1:1.8.2"})
        inflow_data = [obs.Volume for obs in inflow_observations]
    if (len(consumptionvaluesupload.Outflows) > 0):
        outflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                             consumptionvaluesupload.Outflows)
        counterstand_of_outflow_at_start = parser.get_counter_stand(startdatetime, counterstandsupload,
                                                                    consumptionvaluesupload.Outflows,
                                                                    {"1-1:2.8.1", "1-1:2.8.2"})

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
        'counterstandOfInflowAtStart': counterstand_of_inflow_at_start,
        'counterstandOfOutflowAtStart': counterstand_of_outflow_at_start,
        'totalInflow': total_inflow,
        'totalOutflow': total_outflow,
        'procentInflow': procent_inflow,
        'procentOutflow': procent_outflow,
        "startdatetime": startdatetime,
        "enddatetime": enddatetime,
    }

    return jsonify(data)


def find_start_and_end_datetime(inflow_and_outflow, counterstands):
    if not inflow_and_outflow.Inflows:
        raise ValueError("No inflows available to determine startdatetime")

    # Step 1: The startdatetime is taken from the first inflow item
    initial_startdatetime = inflow_and_outflow.Inflows[0].StartDateTime

    # Step 2: Find the next suitable enddatetime in counterstands that is after initial_startdatetime
    startdatetime = None
    for counterstand in counterstands:
        for time_period in counterstand.timePeriods:
            if time_period.end > initial_startdatetime:
                startdatetime = time_period.end
                break
        if startdatetime:
            break

    if startdatetime is None:
        raise ValueError("No suitable counterstand found after the initial startdatetime")

    # Step 3: The enddatetime is the last enddate of the last item in the inflows list
    enddatetime = inflow_and_outflow.Inflows[-1].EndDateTime

    return startdatetime, enddatetime


@app.route('/post-data', methods=['POST'])
def post_data():
    parser = Parser()
    converter = Converter()

    # Parse data for all sensor IDs
    counterstands = parser.parse_counterstands()

    # Create JSON data for all sensors
    json_data = BytesIO()
    converter.export_to_json(counterstands, json_data)
    json_data.seek(0)

    # Read the JSON data
    data = json_data.getvalue()

    # URL of the server to send the data to
    target_url = "https://example.com/api/receive-data"  # Replace with actual server URL

    try:
        # Send POST request to the target server
        response = requests.post(target_url, data=data, headers={'Content-Type': 'application/json'})

        # Check if the request was successful
        if response.status_code == 200:
            return jsonify({"message": "Data sent successfully", "server_response": response.json()}), 200
        else:
            return jsonify({"error": "Failed to send data", "status_code": response.status_code}), 500

    except requests.RequestException as e:
        return jsonify({"error": "Request failed", "details": str(e)}), 500


if __name__ == '__main__':
    app.run()
