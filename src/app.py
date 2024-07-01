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

    inflow_observations = parser.getObservationsForASpecificDuraction(startdatetime, enddatetime,
                                                                      consumptionvalues.Inflows)
    outflow_observations = parser.getObservationsForASpecificDuraction(startdatetime, enddatetime,
                                                                       consumptionvalues.Outflows)
    counterstand_of_inflow_at_start = parser.getCounterStand(startdatetime, counterstands, consumptionvalues.Inflows,
                                                             {"1-1:1.8.1", "1-1:1.8.2"})
    counterstand_of_outflow_at_start = parser.getCounterStand(startdatetime, counterstands, consumptionvalues.Outflows,
                                                              {"1-1:2.8.1", "1-1:2.8.2"})

    inflow_data = [obs.Volume for obs in inflow_observations]
    outflow_data = [obs.Volume for obs in outflow_observations]
    time_labels = [(startdatetime + timedelta(minutes=15 * i)).strftime('%Y-%m-%d %H:%M') for i in
                   range(len(inflow_data))]

    data = {
        'inflowData': inflow_data,
        'outflowData': outflow_data,
        'timeLabels': time_labels,
        'counterstandOfInflowAtStart': counterstand_of_inflow_at_start,
        'counterstandOfOutflowAtStart': counterstand_of_outflow_at_start
    }

    return jsonify(data)


if __name__ == '__main__':
    app.run()