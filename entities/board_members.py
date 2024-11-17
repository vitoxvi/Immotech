from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
board_member_bp = Blueprint('board_member', __name__)
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


# CREATE a new board member
@board_member_bp.route('/board_members', methods=['POST'])
def create_board_member():
    data = request.json
    id = data.get('id')
    role = data.get('role')

    if not id or not role:
        return jsonify({"error": "Board member ID and role are required"}), 400

    query = """
    INSERT INTO BoardMember (id, role)
    VALUES (?, ?)
    """
    result = query_db(query, (id, role), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Board member created successfully"}), 201


# READ all board members
@board_member_bp.route('/board_members', methods=['GET'])
def get_all_board_members():
    query = "SELECT * FROM BoardMember"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    board_members = [dict(row) for row in result]
    return jsonify(board_members), 200


# READ a single board member by ID
@board_member_bp.route('/board_members/<int:board_member_id>', methods=['GET'])
def get_board_member(board_member_id):
    query = "SELECT * FROM BoardMember WHERE id = ?"
    result = query_db(query, (board_member_id,), one=True)
    if not result:
        return jsonify({"error": "Board member not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing board member
@board_member_bp.route('/board_members/<int:board_member_id>', methods=['PUT'])
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
@board_member_bp.route('/board_members/<int:board_member_id>', methods=['DELETE'])
def delete_board_member(board_member_id):
    query = "DELETE FROM BoardMember WHERE id = ?"
    result = query_db(query, (board_member_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Board member deleted successfully"}), 200
