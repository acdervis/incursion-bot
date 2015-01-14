from flask import Flask
from flask import request
import handler
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def response():
    data = request.get_json()
    return handler.process(data)

if __name__ == "__main__":
    app.debug = True
    app.run()