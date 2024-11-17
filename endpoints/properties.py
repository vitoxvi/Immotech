from flask import Blueprint, request, jsonify
import sqlite3

property_bp = Blueprint('property', __name__)
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


# CREATE a new property
@property_bp.route('/properties', methods=['POST'])
def create_property():
    data = request.json
    name = data.get('name')
    address = data.get('address')
    property_document = data.get('property_document')  # Optional

    if not name or not address:
        return jsonify({"error": "Name and address are required"}), 400

    query = """
    INSERT INTO Property (name, address, property_document)
    VALUES (?, ?, ?)
    """
    result = query_db(query, (name, address, property_document), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Property created successfully"}), 201


# READ all properties
@property_bp.route('/properties', methods=['GET'])
def get_all_properties():
    query = "SELECT * FROM Property"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    properties = [dict(row) for row in result]
    return jsonify(properties), 200


# READ a single property by ID
@property_bp.route('/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    query = "SELECT * FROM Property WHERE id = ?"
    result = query_db(query, (property_id,), one=True)
    if not result:
        return jsonify({"error": "Property not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing property
@property_bp.route('/properties/<int:property_id>', methods=['PUT'])
def update_property(property_id):
    data = request.json
    name = data.get('name')
    address = data.get('address')
    property_document = data.get('property_document')  # Optional

    if not name or not address:
        return jsonify({"error": "Name and address are required"}), 400

    query = """
    UPDATE Property
    SET name = ?, address = ?, property_document = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (name, address, property_document, property_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Property updated successfully"}), 200


# DELETE a property
@property_bp.route('/properties/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    query = "DELETE FROM Property WHERE id = ?"
    result = query_db(query, (property_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Property deleted successfully"}), 200