from datetime import datetime

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


if __name__ == '__main__':
    app.run()
