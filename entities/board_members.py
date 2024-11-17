from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
board_member_bp = Blueprint('board_member', __name__)
DATABASE = 'database.db'


# Helper function to interact with the database
def query_db(query, args=(), one=False, commit=False, return_last_id=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            if return_last_id:
                result = {"id": cursor.lastrowid}
            else:
                result = {"status": "success"}
        else:
            result = cursor.fetchall()
    except sqlite3.Error as e:
        result = {"error": str(e)}
    finally:
        conn.close()
    return (result[0] if result else None) if one and not commit else result


@board_member_bp.route('/backend/board_members', methods=['POST'])
def create_board_member():
    data = request.json

    # Person attributes
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')
    phone_number = data.get('phone_number')
    email = data.get('email')
    bank_correspondence = data.get('bank_correspondence')

    # BoardMember attributes
    role = data.get('role')

    # Validate required fields
    if not all([first_name, last_name, role]):
        return jsonify({"error": "First name, last name, and role are required"}), 400

    # Step 1: Create Person
    person_query = """
    INSERT INTO Person (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    person_result = query_db(
        person_query,
        (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence),
        commit=True,
        return_last_id=True  # Fetch last inserted ID
    )

    if "error" in person_result:
        return jsonify(person_result), 500

    person_id = person_result.get("id")
    if not person_id:
        return jsonify({"error": "Failed to create person, person ID not generated"}), 500

    # Step 2: Create BoardMember linked to the Person
    board_member_query = """
    INSERT INTO BoardMember (id, role)
    VALUES (?, ?)
    """
    board_member_result = query_db(
        board_member_query,
        (person_id, role),
        commit=True
    )

    if "error" in board_member_result:
        return jsonify(board_member_result), 500

    return jsonify({
        "message": "Board member and associated Person created successfully",
        "person_id": person_id,
        "board_member_id": person_id  # Assuming BoardMember ID matches Person ID
    }), 201



# READ all board members
@board_member_bp.route('/backend/board_members', methods=['GET'])
def get_all_board_members():
    query = """
    SELECT 
        BoardMember.id AS board_member_id, 
        BoardMember.role, 
        Person.first_name, 
        Person.last_name, 
        Person.date_of_birth, 
        Person.address, 
        Person.phone_number, 
        Person.email, 
        Person.bank_correspondence
    FROM BoardMember
    JOIN Person ON BoardMember.id = Person.id
    """
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    board_members = [dict(row) for row in result]
    return jsonify(board_members), 200


# READ a single board member
@board_member_bp.route('/backend/board_members/<int:board_member_id>', methods=['GET'])
def get_board_member(board_member_id):
    query = """
    SELECT 
        BoardMember.id AS board_member_id, 
        BoardMember.role, 
        Person.first_name, 
        Person.last_name, 
        Person.date_of_birth, 
        Person.address, 
        Person.phone_number, 
        Person.email, 
        Person.bank_correspondence
    FROM BoardMember
    JOIN Person ON BoardMember.id = Person.id
    WHERE BoardMember.id = ?
    """
    result = query_db(query, (board_member_id,), one=True)
    if not result:
        return jsonify({"error": "Board member not found"}), 404

    return jsonify(dict(result)), 200



# UPDATE an existing board member
@board_member_bp.route('/backend/board_members/<int:board_member_id>', methods=['PUT'])
def update_board_member(board_member_id):
    data = request.json
    role = data.get('role')

    if not role:
        return jsonify({"error": "Role is required"}), 400

    query = """
    UPDATE BoardMember
    SET role = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (role, board_member_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Board member updated successfully"}), 200


# DELETE a board member
@board_member_bp.route('/backend/board_members/<int:board_member_id>', methods=['DELETE'])
def delete_board_member(board_member_id):
    query = "DELETE FROM BoardMember WHERE id = ?"
    result = query_db(query, (board_member_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Board member deleted successfully"}), 200
