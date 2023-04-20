from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")