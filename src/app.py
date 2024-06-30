import json
from datetime import datetime, timedelta

from flask import Flask, render_template, jsonify

from src.parser import Parser

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here

    pass


@app.route('/ui')
def ui():
    return render_template('frontend/index.html')


@app.route('/chart')
def chart():
    return render_template('frontend/chart.html')


@app.route('/chart/data')
def chart_data():
    parser = Parser()

    counterstands = parser.parse_counterstands()
    consumptionvalues = parser.parse_consumptionvalues()
    startdatetime = datetime(2019, 3, 20, 23, 0)
    enddatetime = datetime(2019, 3, 21, 23, 30)

    inflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                      consumptionvalues.Inflows)
    outflow_observations = parser.get_observations_for_specific_duration(startdatetime, enddatetime,
                                                                       consumptionvalues.Outflows)
    counterstand_of_inflow_at_start = parser.get_counterstand(startdatetime, counterstands, consumptionvalues.Inflows)

    inflow_data = [obs.Volume for obs in inflow_observations]
    outflow_data = [obs.Volume for obs in outflow_observations]
    time_labels = [(startdatetime + timedelta(minutes=15 * i)).strftime('%Y-%m-%d %H:%M') for i in
                   range(len(inflow_data))]

    total_inflow = sum(obs.Volume for obs in inflow_observations)
    total_outflow = sum(obs.Volume for obs in outflow_observations)

    # Calculate average growth, example logic
    all_time_inflow = parser.get_all_time_total(consumptionvalues.Inflows)
    average_growth = (total_inflow - all_time_inflow) / all_time_inflow * 100 if all_time_inflow != 0 else 0

    data = {
        'totalInflow': total_inflow,
        'totalOutflow': total_outflow,
        'averageGrowth': average_growth,
        'inflowData': inflow_data,
        'outflowData': outflow_data,
        'timeLabels': time_labels,
        'counterstandOfInflowAtStart': counterstand_of_inflow_at_start
    }

    return jsonify(data)



if __name__ == '__main__':
    app.run()