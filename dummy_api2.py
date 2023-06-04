from flask import Flask, jsonify

app = Flask(__name__)

# Dummy list data
dummy_list = ["samsung", "apple", "vivo", "mi"]

@app.route('/api/list', methods=['GET'])
def get_list():
    return jsonify(dummy_list)

if __name__ == '__main__':
    port = 9001
    app.run(port=port)