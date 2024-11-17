from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
person_bp = Blueprint('person', __name__)
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


# CREATE a new person
@person_bp.route('/persons', methods=['POST'])
def create_person():
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')
    phone_number = data.get('phone_number')
    email = data.get('email')
    bank_correspondence = data.get('bank_correspondence')

    if not all([first_name, last_name]):
        return jsonify({"error": "First name and last name are required"}), 400

    query = """
    INSERT INTO Person (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    result = query_db(
        query,
        (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence),
        commit=True
    )
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Person created successfully"}), 201


# READ all persons
@person_bp.route('/persons', methods=['GET'])
def get_all_persons():
    query = "SELECT * FROM Person"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    persons = [dict(row) for row in result]
    return jsonify(persons), 200


# READ a single person by ID
@person_bp.route('/persons/<int:person_id>', methods=['GET'])
def get_person(person_id):
    query = "SELECT * FROM Person WHERE id = ?"
    result = query_db(query, (person_id,), one=True)
    if not result:
        return jsonify({"error": "Person not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing person
@person_bp.route('/persons/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')
    phone_number = data.get('phone_number')
    email = data.get('email')
    bank_correspondence = data.get('bank_correspondence')

    if not all([first_name, last_name]):
        return jsonify({"error": "First name and last name are required"}), 400

    query = """
    UPDATE Person
    SET first_name = ?, last_name = ?, date_of_birth = ?, address = ?, phone_number = ?, email = ?, bank_correspondence = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(
        query,
        (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence, person_id),
        commit=True
    )
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Person updated successfully"}), 200


# DELETE a person
@person_bp.route('/persons/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    query = "DELETE FROM Person WHERE id = ?"
    result = query_db(query, (person_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Person deleted successfully"}), 200
