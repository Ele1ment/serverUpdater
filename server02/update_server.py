from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/check_update', methods=['POST'])
def check_update():
    data = request.get_json()
    current_version = data.get('current_version')

    # Логика проверки обновлений
    latest_version = "1.2.3"
    update_url = "http://yourserver.com/download/latest_version.zip"

    if current_version != latest_version:
        return jsonify({"status": "update_available", "latest_version": latest_version, "url": update_url}), 200
    return jsonify({"status": "up_to_date"}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
