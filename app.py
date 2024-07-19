from flask import Flask, request, jsonify, send_from_directory
from geopy.distance import geodesic
from datetime import datetime
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# In-memory storage for attendance records and radius
attendance_records = []
users = [
    {"user_id": "1", "name": "Alice", "center_location": (51.505, -0.09)},
    {"user_id": "2", "name": "Bob", "center_location": (51.515, -0.10)}
]

# Default radius (in kilometers)
RADIUS = 0.5

# Initialize BackgroundScheduler
scheduler = BackgroundScheduler()

# Function to export attendance to Excel
def export_to_excel(records):
    try:
        df = pd.DataFrame(records)
        df.to_excel('backend/data/attendance.xlsx', index=False)
        print("Attendance exported successfully.")
    except Exception as e:
        print(f"Error exporting attendance: {str(e)}")

# Schedule the export task to run every 10 seconds
scheduler.add_job(export_to_excel, 'interval', seconds=10, args=[attendance_records])

# Start the scheduler
scheduler.start()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    user_id = data['user_id']
    user_location = (data['latitude'], data['longitude'])
    
    user = next((u for u in users if u['user_id'] == user_id), None)
    if not user:
        return jsonify({'status': 'Invalid user ID'}), 400
    
    center_location = user['center_location']
    # Check if the user is within the geofenced area
    distance = geodesic(center_location, user_location).km
    status = 'Present' if distance <= RADIUS else 'Absent'
    
    # Create an attendance record
    attendance_record = {
        'user_id': user_id,
        'name': user['name'],
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'status': status
    }
    attendance_records.append(attendance_record)
    
    return jsonify({'status': status, 'center_location': center_location, 'radius': RADIUS})

@app.route('/get-attendance', methods=['GET'])
def get_attendance():
    return jsonify(attendance_records)

@app.route('/export-attendance', methods=['GET'])
def export_attendance():
    export_to_excel(attendance_records)
    return jsonify({'message': 'Attendance exported to attendance.xlsx'})

@app.route('/set-center', methods=['POST'])
def set_center():
    data = request.json
    user_id = data['user_id']
    latitude = data['latitude']
    longitude = data['longitude']

    user = next((u for u in users if u['user_id'] == user_id), None)
    if not user:
        return jsonify({'message': 'Invalid user ID'}), 400
    
    user['center_location'] = (latitude, longitude)
    return jsonify({'message': 'Geofence center updated successfully'})

@app.route('/set-radius', methods=['POST'])
def set_radius():
    global RADIUS
    RADIUS = request.json['radius']
    return jsonify({'message': 'Geofence radius updated successfully'})

@app.route('/get-users', methods=['GET'])
def get_users():
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True)
