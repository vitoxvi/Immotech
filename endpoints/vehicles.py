from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
vehicle_bp = Blueprint('vehicle', __name__)
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


# CREATE a new vehicle
@vehicle_bp.route('/backend/vehicles', methods=['POST'])
def create_vehicle():
    data = request.json
    name = data.get('name')
    license_plate = data.get('license_plate')
    vehicle_document = data.get('vehicle_document')  # Optional, may be binary data

    if not name:
        return jsonify({"error": "Vehicle name is required"}), 400

    query = """
    INSERT INTO Vehicle (name, license_plate, vehicle_document)
    VALUES (?, ?, ?)
    """
    result = query_db(query, (name, license_plate, vehicle_document), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Vehicle created successfully"}), 201


#Fetch one or multiple vehicles
@vehicle_bp.route('/backend/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicles(vehicle_id):
    if vehicle_id == 0:
        # Fetch all vehicles
        query = "SELECT * FROM Vehicle"
        result = query_db(query)
        if "error" in result:
            return jsonify(result), 500
        vehicles = [dict(row) for row in result]
        return jsonify(vehicles), 200
    else:
        # Fetch a specific vehicle by ID
        query = "SELECT * FROM Vehicle WHERE id = ?"
        result = query_db(query, (vehicle_id,), one=True)
        if not result:
            return jsonify([]), 200  # Return an empty array if not found
        return jsonify([dict(result)]), 200  # Wrap the single result in an array



# UPDATE an existing vehicle
@vehicle_bp.route('/backend/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    data = request.json
    name = data.get('name')
    license_plate = data.get('license_plate')
    vehicle_document = data.get('vehicle_document')  # Optional, may be binary data

    if not name:
        return jsonify({"error": "Vehicle name is required"}), 400

    query = """
    UPDATE Vehicle
    SET name = ?, license_plate = ?, vehicle_document = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (name, license_plate, vehicle_document, vehicle_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Vehicle updated successfully"}), 200


# DELETE a vehicle
@vehicle_bp.route('/backend/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    query = "DELETE FROM Vehicle WHERE id = ?"
    result = query_db(query, (vehicle_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Vehicle deleted successfully"}), 200
