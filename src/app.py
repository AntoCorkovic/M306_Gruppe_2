import json
from datetime import datetime, timedelta

from flask import Flask, render_template

from src.parser import Parser

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    parser = Parser()

    counterstands = parser.parse_counterstands()
    try:
        consumptionvalues = parser.parse_consumptionvalues()
    except Exception as e:
        print(e)

    startdatetime = datetime(2019, 3, 20, 23, 0)
    enddatetime = datetime(2019, 3, 26, 23, 30)
    inflowObservationvalues = parser.getObservationsForASpecificDuraction(startdatetime, enddatetime, consumptionvalues.Inflows)
    outflowsObservationvalues = parser.getObservationsForASpecificDuraction(startdatetime, enddatetime, consumptionvalues.Outflows)
    counterstandOfInflowAtStart = parser.getCounterStand(startdatetime, counterstands, consumptionvalues.Inflows)

    return 'Hello World!'


@app.route('/ui')
def ui():  # put application's code here


    return render_template('frontend/index.html')

@app.route('/chart')
def chart():
    parser = Parser()

    counterstands = parser.parse_counterstands()
    consumptionvalues = parser.parse_consumptionvalues()
    startdatetime = datetime(2019, 3, 20, 23, 0)
    enddatetime = datetime(2019, 3, 21, 23, 30)

    inflowObservations = parser.getObservationsForASpecificDuraction(startdatetime, enddatetime,
                                                                     consumptionvalues.Inflows)
    outflowObservations = parser.getObservationsForASpecificDuraction(startdatetime, enddatetime,
                                                                      consumptionvalues.Outflows)
    counterstandOfInflowAtStart = parser.getCounterStand(startdatetime, counterstands, consumptionvalues.Inflows)

    # Extrahieren der Volumendaten und Zeitlabels
    inflowData = [obs.Volume for obs in inflowObservations]
    outflowData = [obs.Volume for obs in outflowObservations]
    timeLabels = [(startdatetime + timedelta(minutes=15 * i)).strftime('%Y-%m-%d %H:%M') for i in
                  range(len(inflowData))]

    # Daten in einem Dictionary speichern
    data = {
        'inflowData': inflowData,
        'outflowData': outflowData,
        'timeLabels': timeLabels,
        'counterstandOfInflowAtStart': counterstandOfInflowAtStart
    }

    # Daten direkt an das Template übergeben
    return render_template('frontend/chart.html', data=json.dumps(data))

if __name__ == '__main__':
    app.run()
