from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import string
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LicensingDB.db'
db = SQLAlchemy(app)

# Модель для лицензий
class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    LicenseKey = db.Column(db.String(255), unique=True, nullable=False)
    CreatedDate = db.Column(db.DateTime, nullable=False)
    days_valid = db.Column(db.Integer, nullable=False)
    HWID = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)


# Проверка лицензии
@app.route('/check_license', methods=['POST'])
def check_license():
    data = request.get_json()
    license_key = data.get('license_key')
    license_entry = License.query.filter_by(LicenseKey=license_key).first()
    
    if license_entry:
        if license_entry.end_date and license_entry.end_date < datetime.now():
            return jsonify({"status": "expired"}), 403  # Лицензия истекла
        return jsonify({"status": "valid"}), 200  # Лицензия действительна
    return jsonify({"status": "invalid"}), 404  # Лицензия недействительна


# Активация лицензии
@app.route('/activate_key', methods=['POST'])
def activate_key():
    data = request.get_json()
    license_key = data.get('license_key')
    hwid = data.get('hwid')
    
    license_entry = License.query.filter_by(LicenseKey=license_key).first()
    
    if license_entry:
        if license_entry.HWID is None:
            license_entry.HWID = hwid
            license_entry.start_date = datetime.now()
            license_entry.end_date = license_entry.start_date + timedelta(days=license_entry.days_valid)
            db.session.commit()
            return jsonify({"status": "activated"}), 200
        
        if license_entry.HWID == hwid:
            return jsonify({"status": "already_activated", "message": "Key is already activated for this HWID."}), 200
        
        return jsonify({"status": "activation_failed", "message": "Key is already activated for a different HWID."}), 403

    return jsonify({"status": "activation_failed", "message": "License key not found."}), 404


# Генерация лицензий
@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    data = request.json
    count = data.get('count', 1)
    days_valid = data.get('days_valid', 30)
    hwid = data.get('hwid')

    allowed_hwid = "1A1b@C3d#E5f&G7h*J9k!L0m^N2o(P4q)R6s+T8u"
    
    if hwid != allowed_hwid:
        return jsonify({"status": "failed", "message": "Invalid HWID"}), 403

    keys = []
    for _ in range(count):
        key = generate_license_key()
        new_license = License(LicenseKey=key, CreatedDate=datetime.now(), days_valid=days_valid)
        db.session.add(new_license)
        keys.append(key)
    
    db.session.commit()
    return jsonify({"keys": keys}), 201


def generate_license_key(length=26):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


# Проверка обновления
CURRENT_VERSION = "1.0.1"

@app.route('/check_update', methods=['POST'])
def check_update():
    data = request.get_json()
    client_version = data.get('version')

    if client_version != CURRENT_VERSION:
        return jsonify({"update_available": True, "version": CURRENT_VERSION}), 200
    else:
        return jsonify({"update_available": False}), 200


# Скачивание обновления
@app.route('/download_update', methods=['GET'])
def download_update():
    update_file_path = "path_to_your_update_file/update.zip"
    if os.path.exists(update_file_path):
        return send_file(update_file_path, as_attachment=True)
    else:
        return jsonify({"error": "Update file not found"}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаем таблицы в базе данных, если они не существуют
    app.run(host='0.0.0.0', port=5000, debug=True)
