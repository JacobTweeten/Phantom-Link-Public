
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api')
def index():
    return jsonify({"message": "Welcome to Phantom-Link!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)