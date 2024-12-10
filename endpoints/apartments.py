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


#READ all apartments with optional filters
@apartment_bp.route('/backend/apartments', methods=['GET'])
def get_all_apartments():
    # Retrieve optional filters from query parameters
    unit_id = request.args.get('unit_id')
    property_id = request.args.get('property_id')

    # Base query with necessary joins
    query = """
    SELECT 
        Apartment.id AS apartment_id,
        Apartment.size_sqm,
        Apartment.rent,
        Apartment.rooms,
        Apartment.designation,
        Apartment.unit_id,
        Unit.name AS unit_name,
        Unit.address AS unit_address,
        Property.id AS property_id,
        Property.name AS property_name,
        Property.address AS property_address
    FROM Apartment
    LEFT JOIN Unit ON Apartment.unit_id = Unit.id
    LEFT JOIN Property ON Unit.property_id = Property.id
    WHERE 1 = 1
    """
    filters = []

    # Add optional filters dynamically
    if unit_id:
        query += " AND Unit.id = ?"
        filters.append(unit_id)
    if property_id:
        query += " AND Property.id = ?"
        filters.append(property_id)

    try:
        # Execute the query with the filters
        result = query_db(query, tuple(filters))
        if "error" in result:
            return jsonify(result), 500

        # Convert results to a list of dictionaries and return as JSON
        apartments = [dict(row) for row in result]
        return jsonify(apartments), 200
    except Exception as e:
        # Handle errors gracefully
        return jsonify({"error": str(e)}), 500



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
    try:
        # Parse parameters
        size_sqm = str(data.get('size_sqm'))  # Ensure it's a string for TEXT type
        rent = float(data.get('rent'))  # Ensure rent is a valid float
        rooms = int(data.get('rooms')) if data.get('rooms') is not None else 0

        # Validate required fields
        if not all([size_sqm, rent, rooms]):
            return jsonify({"error": "All required fields must be provided"}), 400


        # Update the apartment in the database
        query = """
        UPDATE Apartment
        SET size_sqm = ?, rent = ?, rooms = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        result = query_db(query, (size_sqm, rent, rooms, apartment_id), commit=True)
        if "error" in result:
            print("Database error:", result)
            return jsonify(result), 500

        return jsonify({"message": "Apartment updated successfully"}), 200

    except Exception as e:
        print("Error updating apartment:", e)
        return jsonify({"error": str(e)}), 500



# DELETE an apartment
@apartment_bp.route('/backend/apartments/<int:apartment_id>', methods=['DELETE'])
def delete_apartment(apartment_id):
    query = "DELETE FROM Apartment WHERE id = ?"
    result = query_db(query, (apartment_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Apartment deleted successfully"}), 200
