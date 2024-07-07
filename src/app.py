from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, send_file
from io import BytesIO
from converter import Converter
from src.parser import Parser

app = Flask(__name__)

counterstands = None
consumptionvalues = None


@app.route('/download/csv')
def download_csv():
    global counterstands
    if counterstands is None:
        return jsonify({"error": "Data not loaded"}), 400

    converter = Converter()
    output = BytesIO()
    converter.export_counterstands_to_csv(counterstands, output)
    output.seek(0)
    return send_file(output,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='counterstands.csv')

@app.route('/download/json')
def download_json():
    global counterstands
    if counterstands is None:
        return jsonify({"error": "Data not loaded"}), 400

    converter = Converter()
    output = BytesIO()
    converter.export_counterstands_to_json(counterstands, output)
    output.seek(0)
    return send_file(output,
                     mimetype='application/json',
                     as_attachment=True,
                     download_name='counterstands.json')


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


if __name__ == '__main__':
    app.run()
