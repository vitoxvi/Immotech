from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
vehicle_usage_log_bp = Blueprint('vehicle_usage_log', __name__)
DATABASE = 'database.db'


# Helper function to interact with the database
def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            result = {"status": "success"}
        else:
            result = cursor.fetchall()
    except sqlite3.Error as e:
        result = {"error": str(e)}
    finally:
        conn.close()
    return (result[0] if result else None) if one and not commit else result


# CREATE a new vehicle usage log
@vehicle_usage_log_bp.route('/vehicle_usage_logs', methods=['POST'])
def create_vehicle_usage_log():
    data = request.json
    vehicle_id = data.get('vehicle_id')
    employee_id = data.get('employee_id')
    date_of_usage = data.get('date_of_usage')
    purpose = data.get('purpose', 'Other')  # Default to 'Other'
    distance_travelled = data.get('distance_travelled', 0)  # Default to 0

    if not all([vehicle_id, employee_id, date_of_usage]):
        return jsonify({"error": "Vehicle ID, employee ID, and date of usage are required"}), 400

    query = """
    INSERT INTO VehicleUsageLog (vehicle_id, employee_id, date_of_usage, purpose, distance_travelled)
    VALUES (?, ?, ?, ?, ?)
    """
    result = query_db(query, (vehicle_id, employee_id, date_of_usage, purpose, distance_travelled), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Vehicle usage log created successfully"}), 201


# READ all vehicle usage logs
@vehicle_usage_log_bp.route('/vehicle_usage_logs', methods=['GET'])
def get_all_vehicle_usage_logs():
    query = "SELECT * FROM VehicleUsageLog"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    vehicle_usage_logs = [dict(row) for row in result]
    return jsonify(vehicle_usage_logs), 200


# READ a single vehicle usage log by ID
@vehicle_usage_log_bp.route('/vehicle_usage_logs/<int:log_id>', methods=['GET'])
def get_vehicle_usage_log(log_id):
    query = "SELECT * FROM VehicleUsageLog WHERE id = ?"
    result = query_db(query, (log_id,), one=True)
    if not result:
        return jsonify({"error": "Vehicle usage log not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing vehicle usage log
@vehicle_usage_log_bp.route('/vehicle_usage_logs/<int:log_id>', methods=['PUT'])
def update_vehicle_usage_log(log_id):
    data = request.json
    vehicle_id = data.get('vehicle_id')
    employee_id = data.get('employee_id')
    date_of_usage = data.get('date_of_usage')
    purpose = data.get('purpose')
    distance_travelled = data.get('distance_travelled')

    if not all([vehicle_id, employee_id, date_of_usage]):
        return jsonify({"error": "Vehicle ID, employee ID, and date of usage are required"}), 400

    query = """
    UPDATE VehicleUsageLog
    SET vehicle_id = ?, employee_id = ?, date_of_usage = ?, purpose = ?, distance_travelled = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (vehicle_id, employee_id, date_of_usage, purpose, distance_travelled, log_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Vehicle usage log updated successfully"}), 200


# DELETE a vehicle usage log
@vehicle_usage_log_bp.route('/vehicle_usage_logs/<int:log_id>', methods=['DELETE'])
def delete_vehicle_usage_log(log_id):
    query = "DELETE FROM VehicleUsageLog WHERE id = ?"
    result = query_db(query, (log_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Vehicle usage log deleted successfully"}), 200
