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


#create appartment
@apartment_bp.route('/backend/apartments', methods=['POST'])
def create_apartment():
    data = request.json
    try:
        # Parse parameters
        size_sqm = str(data.get('size_sqm'))  # Ensure it's a string for TEXT type
        rent = float(data.get('rent'))  # Ensure rent is a valid float
        rooms = int(data.get('rooms')) if data.get('rooms') is not None else 0
        unit_id = int(data.get('unit_id')) if data.get('unit_id') else None  # Updated

        # Validate required fields
        if not all([size_sqm, rent, unit_id]):
            return jsonify({"error": "All required fields must be provided"}), 400
        



        # Log parameters
        print(f"Inserting apartment: size_sqm={size_sqm}, rent={rent}, rooms={rooms}, unit_id={unit_id}")

        # Validate that the unit_id exists
        unit_check_query = "SELECT id FROM Unit WHERE id = ?"
        unit_exists = query_db(unit_check_query, (unit_id,), one=True)
        if not unit_exists:
            return jsonify({"error": f"Unit ID {unit_id} does not exist"}), 400


        # Insert into Apartment table
        query = """
        INSERT INTO Apartment (size_sqm, rent, rooms, unit_id)
        VALUES (?, ?, ?, ?)
        """
        result = query_db(query, (size_sqm, rent, rooms, unit_id), commit=True)

        if "error" in result:
            print("Database error:", result)
            return jsonify(result), 500

        return jsonify({"message": "Apartment created successfully"}), 201

    except Exception as e:
        print("Error creating apartment:", e)
        return jsonify({"error": str(e)}), 500


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
    rooms = rooms = int(data.get('rooms')) if data.get('rooms') is not None else 0

    address = data.get('address')
    property_id = data.get('property_id')

    if not all([size_sqm, rent, address, property_id]):
        return jsonify({"error": "All required fields must be provided"}), 400

    query = """
    UPDATE Apartment
    SET size_sqm = ?, rent = ?, rooms = ?, address = ?,  property_id = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (size_sqm, rent, rooms, address, property_id, apartment_id), commit=True)
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
