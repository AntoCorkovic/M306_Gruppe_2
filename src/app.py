from flask import Flask

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
    print(consumptionvalues)



    return 'Hello World!'


if __name__ == '__main__':
    app.run()
