from flask import Flask

from powerstream.src.parser import Parser

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    parser = Parser()

    #outflow_data = parser.parse_Outflow()
    try:
        inflow_data = parser.parse_Inflow()
    except Exception as e:
        print(e)
    print(inflow_data)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
