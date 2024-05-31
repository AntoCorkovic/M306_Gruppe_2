from flask import Flask

from src.parser import Parser

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    parser = Parser()
    file_path = r'C:\Users\janis\PycharmProjects\ESL-Files\EdmRegisterWertExport_20190131_eslevu_20190322160349.xml'
    outflow_data = parser.parse_Outflow(file_path)
    inflow_data = parser.parse_Inflow(file_path)
    print(inflow_data)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
