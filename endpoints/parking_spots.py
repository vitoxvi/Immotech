from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
parking_spot_bp = Blueprint('parking_spot', __name__)
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


# CREATE a new parking spot
@parking_spot_bp.route('/backend/parking_spots', methods=['POST'])
def create_parking_spot():
    data = request.json
    rent = data.get('rent')
    spot_number = data.get('spot_number')
    type_ = data.get('type')
    property_id = data.get('property_id')

    if not all([rent, spot_number, type_, property_id]):
        return jsonify({"error": "All required fields must be provided"}), 400

    query = """
    INSERT INTO ParkingSpot (rent, spot_number, type, property_id)
    VALUES (?, ?, ?, ?)
    """
    result = query_db(query, (rent, spot_number, type_, property_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Parking spot created successfully"}), 201


# READ all parking spots with optional filtering by property ID
@parking_spot_bp.route('/backend/parking_spots', methods=['GET'])
def get_all_parking_spots():
    property_id = request.args.get('property_id')
    if property_id:
        query = "SELECT * FROM ParkingSpot WHERE property_id = ?"
        result = query_db(query, (property_id,))
    else:
        query = "SELECT * FROM ParkingSpot"
        result = query_db(query)

    if "error" in result:
        return jsonify(result), 500

    parking_spots = [dict(row) for row in result]
    return jsonify(parking_spots), 200


# READ a single parking spot by ID
@parking_spot_bp.route('/backend/parking_spots/<int:parking_spot_id>', methods=['GET'])
def get_parking_spot(parking_spot_id):
    query = "SELECT * FROM ParkingSpot WHERE id = ?"
    result = query_db(query, (parking_spot_id,), one=True)
    if not result:
        return jsonify({"error": "Parking spot not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing parking spot
@parking_spot_bp.route('/backend/parking_spots/<int:parking_spot_id>', methods=['PUT'])
def update_parking_spot(parking_spot_id):
    data = request.json
    rent = data.get('rent')
    spot_number = data.get('spot_number')
    type_ = data.get('type')
    property_id = data.get('property_id')

    if not all([rent, spot_number, type_, property_id]):
        return jsonify({"error": "All required fields must be provided"}), 400

    query = """
    UPDATE ParkingSpot
    SET rent = ?, spot_number = ?, type = ?, property_id = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (rent, spot_number, type_, property_id, parking_spot_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Parking spot updated successfully"}), 200


# DELETE a parking spot
@parking_spot_bp.route('/backend/parking_spots/<int:parking_spot_id>', methods=['DELETE'])
def delete_parking_spot(parking_spot_id):
    query = "DELETE FROM ParkingSpot WHERE id = ?"
    result = query_db(query, (parking_spot_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Parking spot deleted successfully"}), 200
