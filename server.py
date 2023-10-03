from flask import Flask, request, jsonify
import os
import sqlite3
from flask_cors import CORS
import facerec_ipcamera_knn

app = Flask(__name__)
cors = CORS(app, origins="*")
# Configuration
DATABASE_NAME = "facerecorg.db"
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the database table if it doesn't exist
def create_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            staff_id TEXT NOT NULL UNIQUE,
            last_name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# Endpoint 1: Enroll staff
@app.route('/enroll', methods=['POST'])
def enroll():
    try:
        first_name = request.form['first_name']
        staff_id = request.form['staff_id']
        last_name = request.form['last_name']
        department = request.form['department']
        role = request.form['role']

        # Save the images in the specified format
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{last_name} {first_name}")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        for i in range(5):
            image = request.files.get(f'image_{i}')
            if image:
                image.save(os.path.join(folder_path, f'image_{i}.jpg'))

        # Save staff details to the database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO staff (first_name, staff_id, last_name, department, role) VALUES (?, ?, ?, ?, ?)',
                       (first_name, staff_id, last_name, department, role))
        conn.commit()
        conn.close()

        return jsonify({"message": "Staff enrolled successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/staff', methods=['GET'])
def list_staff():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id, first_name, last_name, staff_id, department, role FROM staff')
        staff_data = cursor.fetchall()
        conn.close()

        staff_list = []
        for staff in staff_data:
            staff_dict = {
                "id": staff[0],
                "first_name": staff[1],
                "last_name": staff[2],
                "staff_id": staff[3],
                "department": staff[4],
                "role": staff[5],
                "fullname": f"{staff[2]} {staff[1]}"
            }
            staff_list.append(staff_dict)

        return jsonify(staff_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/train', methods=['POST'])
def train():
    try:
        print("Training KNN classifier...")
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'])
        if os.path.exists(folder_path):   
            classifier = facerec_ipcamera_knn.train(folder_path, model_save_path="trained_knn_model.clf", n_neighbors=2)
            print("Training complete!")
            return jsonify({"message": "Successfully trained all images!"}), 200
        else:
            return jsonify({"message": "Failed: Empty training data!"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 4: Prediction
@app.route('/prediction', methods=['GET'])
def get_predictions():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT timestamp, name FROM predictions')
        prediction_data = cursor.fetchall()
        conn.close()

        prediction_list = []
        for prediction in prediction_data:
            prediction_dict = {
                "timestamp": prediction[0],
                "name": prediction[1]
            }
            prediction_list.append(prediction_dict)

        return jsonify(prediction_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Endpoint 5: Save prediction
@app.route('/prediction', methods=['POST'])
def save_prediction():
    try:
        timestamp = request.json['timestamp']
        name = request.json['name']

        # Save the prediction to the database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO predictions (timestamp, name) VALUES (?, ?)',
                       (timestamp, name))
        conn.commit()
        conn.close()

        return jsonify({"message": "Prediction saved successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
