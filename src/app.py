from flask import Flask, render_template

# from src.parser import Parser

app = Flask(__name__)


@app.route('/')
def hello_world(): 
    # parser = Parser()

    # counterstands = parser.parse_counterstands()
    # try:
    #     consumptionvalues = parser.parse_consumptionvalues()
    # except Exception as e:
    #     print(e)
    # print(consumptionvalues)

    return 'Hello World!'


@app.route('/ui')
def ui():

    return render_template('frontend/index.html')


if __name__ == '__main__':
    app.run()
