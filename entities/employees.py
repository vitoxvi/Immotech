from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
employee_bp = Blueprint('employee', __name__)
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


# CREATE a new employee
@employee_bp.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    id = data.get('id')
    role = data.get('role')
    employment_rate = data.get('employment_rate')

    if not id or not role or not employment_rate:
        return jsonify({"error": "Employee ID, role, and employment rate are required"}), 400

    query = """
    INSERT INTO Employee (id, role, employment_rate)
    VALUES (?, ?, ?)
    """
    result = query_db(query, (id, role, employment_rate), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Employee created successfully"}), 201


# READ all employees
@employee_bp.route('/employees', methods=['GET'])
def get_all_employees():
    query = "SELECT * FROM Employee"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    employees = [dict(row) for row in result]
    return jsonify(employees), 200


# READ a single employee by ID
@employee_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    query = "SELECT * FROM Employee WHERE id = ?"
    result = query_db(query, (employee_id,), one=True)
    if not result:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing employee
@employee_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json
    role = data.get('role')
    employment_rate = data.get('employment_rate')

    if not role or not employment_rate:
        return jsonify({"error": "Role and employment rate are required"}), 400

    query = """
    UPDATE Employee
    SET role = ?, employment_rate = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (role, employment_rate, employee_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Employee updated successfully"}), 200


# DELETE an employee
@employee_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    query = "DELETE FROM Employee WHERE id = ?"
    result = query_db(query, (employee_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Employee deleted successfully"}), 200
