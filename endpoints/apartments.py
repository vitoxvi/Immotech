from flask import Blueprint, request, jsonify
import sqlite3

apartment_bp = Blueprint('apartment', __name__)
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
            result = {"status": "success"}  # Return a status for commit queries
        else:
            result = cursor.fetchall()
    except sqlite3.Error as e:
        result = {"error": str(e)}
    finally:
        conn.close()
    return (result[0] if result else None) if one and not commit else result

# CREATE a new apartment
@apartment_bp.route('/backend/apartments', methods=['POST'])
def create_apartment():
    data = request.json
    size_sqm = data.get('size_sqm')
    rent = data.get('rent')
    rooms = data.get('rooms')
    address = data.get('address')
    unit_number = data.get('unit_number')
    property_id = data.get('property_id')

    if not all([size_sqm, rent, address, unit_number, property_id]):
        return jsonify({"error": "All required fields must be provided"}), 400

    query = """
    INSERT INTO Apartment (size_sqm, rent, rooms, address, unit_number, property_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    result = query_db(query, (size_sqm, rent, rooms, address, unit_number, property_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Apartment created successfully"}), 201


# READ all apartments
@apartment_bp.route('/backend/apartments', methods=['GET'])
def get_all_apartments():
    query = "SELECT * FROM Apartment"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    apartments = [dict(row) for row in result]
    return jsonify(apartments), 200


# READ a single apartment by ID
@apartment_bp.route('/backend/apartments/<int:apartment_id>', methods=['GET'])
def get_apartment(apartment_id):
    query = "SELECT * FROM Apartment WHERE id = ?"
    result = query_db(query, (apartment_id,), one=True)
    if not result:
        return jsonify({"error": "Apartment not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing apartment
@apartment_bp.route('/backend/apartments/<int:apartment_id>', methods=['PUT'])
def update_apartment(apartment_id):
    data = request.json
    size_sqm = data.get('size_sqm')
    rent = data.get('rent')
    rooms = data.get('rooms')
    address = data.get('address')
    unit_number = data.get('unit_number')
    property_id = data.get('property_id')

    if not all([size_sqm, rent, address, unit_number, property_id]):
        return jsonify({"error": "All required fields must be provided"}), 400

    query = """
    UPDATE Apartment
    SET size_sqm = ?, rent = ?, rooms = ?, address = ?, unit_number = ?, property_id = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (size_sqm, rent, rooms, address, unit_number, property_id, apartment_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Apartment updated successfully"}), 200


# DELETE an apartment
@apartment_bp.route('/backend/apartments/<int:apartment_id>', methods=['DELETE'])
def delete_apartment(apartment_id):
    query = "DELETE FROM Apartment WHERE id = ?"
    result = query_db(query, (apartment_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Apartment deleted successfully"}), 200
