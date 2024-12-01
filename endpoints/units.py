from flask import Blueprint, request, jsonify
import sqlite3

unit_bp = Blueprint('unit', __name__)
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


# CREATE a new unit
@unit_bp.route('/backend/units', methods=['POST'])
def create_unit():
    data = request.json
    name = data.get('name')
    address = data.get('address')
    property_id = data.get('property_id')

    if not all([name, address, property_id]):
        return jsonify({"error": "Name, address, and property ID are required"}), 400

    query = """
    INSERT INTO Unit (name, address, property_id)
    VALUES (?, ?, ?)
    """
    result = query_db(query, (name, address, property_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Unit created successfully"}), 201


# READ all units (optionally filter by property ID)
@unit_bp.route('/backend/units', methods=['GET'])
def get_all_units():
    property_id = request.args.get('property_id')
    if property_id:
        query = "SELECT * FROM Unit WHERE property_id = ?"
        result = query_db(query, (property_id,))
    else:
        query = "SELECT * FROM Unit"
        result = query_db(query)

    if "error" in result:
        return jsonify(result), 500

    units = [dict(row) for row in result]
    return jsonify(units), 200


# UPDATE an existing unit
@unit_bp.route('/backend/units/<int:unit_id>', methods=['PUT'])
def update_unit(unit_id):
    data = request.json
    name = data.get('name')
    address = data.get('address')
    property_id = data.get('property_id')

    if not all([name, address, property_id]):
        return jsonify({"error": "Name, address, and property ID are required"}), 400

    query = """
    UPDATE Unit
    SET name = ?, address = ?, property_id = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (name, address, property_id, unit_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Unit updated successfully"}), 200


# DELETE a unit
@unit_bp.route('/backend/units/<int:unit_id>', methods=['DELETE'])
def delete_unit(unit_id):
    query = "DELETE FROM Unit WHERE id = ?"
    result = query_db(query, (unit_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Unit deleted successfully"}), 200
