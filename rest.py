from flask import Flask, jsonify, request

app = Flask(__name__)

data = [
    {
        "Homer": "Simpson",
        "Jeffrey": "Lebowski",
        "Stan": "Smith"
    }
]


@app.route('/data')
def get_incomes():
  return jsonify(data)


@app.route('/data', methods=['POST'])
def add_income():
  data.append(request.get_json())
  return '', 204