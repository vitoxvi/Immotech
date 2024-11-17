from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
employee_bp = Blueprint('employee', __name__)
DATABASE = 'database.db'


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


@employee_bp.route('/backend/employees', methods=['POST'])
def create_employee():
    data = request.json

    # Person attributes
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')
    phone_number = data.get('phone_number')
    email = data.get('email')
    bank_correspondence = data.get('bank_correspondence')

    # Employee attributes
    role = data.get('role')
    employment_rate = data.get('employment_rate')

    # Validate required fields
    if not all([first_name, last_name, role, employment_rate]):
        return jsonify({"error": "Missing required fields"}), 400

    # Step 1: Create Person
    person_query = """
    INSERT INTO Person (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    person_result = query_db(
        person_query,
        (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence),
        commit=True,
        return_last_id=True  # Explicitly fetch last inserted ID
    )

    if "error" in person_result:
        return jsonify(person_result), 500

    person_id = person_result.get("id")
    if not person_id:
        return jsonify({"error": "Failed to create person, person ID not generated"}), 500

    # Step 2: Create Employee linked to the Person
    employee_query = """
    INSERT INTO Employee (id, role, employment_rate)
    VALUES (?, ?, ?)
    """
    employee_result = query_db(
        employee_query,
        (person_id, role, employment_rate),
        commit=True
    )

    if "error" in employee_result:
        return jsonify(employee_result), 500

    return jsonify({
        "message": "Employee and associated Person created successfully",
        "person_id": person_id,
        "employee_id": person_id  # Assuming Employee ID matches Person ID
    }), 201


# READ all employees with person details
@employee_bp.route('/backend/employees', methods=['GET'])
def get_all_employees():
    query = """
    SELECT 
        Employee.id AS employee_id, 
        Employee.role, 
        Employee.employment_rate, 
        Person.first_name, 
        Person.last_name, 
        Person.date_of_birth, 
        Person.address, 
        Person.phone_number, 
        Person.email, 
        Person.bank_correspondence
    FROM Employee
    JOIN Person ON Employee.id = Person.id
    """
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    employees = [dict(row) for row in result]
    return jsonify(employees), 200



# READ a single employee by ID
# READ a single employee by ID with person details
@employee_bp.route('/backend/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    query = """
    SELECT 
        Employee.id AS employee_id, 
        Employee.role, 
        Employee.employment_rate, 
        Person.first_name, 
        Person.last_name, 
        Person.date_of_birth, 
        Person.address, 
        Person.phone_number, 
        Person.email, 
        Person.bank_correspondence
    FROM Employee
    JOIN Person ON Employee.id = Person.id
    WHERE Employee.id = ?
    """
    result = query_db(query, (employee_id,), one=True)
    if not result:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an employee
@employee_bp.route('/backend/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json

    # Optional fields for update
    role = data.get('role')
    employment_rate = data.get('employment_rate')

    # Check if at least one field is provided
    if role is None and employment_rate is None:
        return jsonify({"error": "At least one field (role or employment_rate) must be provided"}), 400

    # Dynamically construct the update query
    query_parts = []
    query_values = []

    if role is not None:
        query_parts.append("role = ?")
        query_values.append(role)

    if employment_rate is not None:
        query_parts.append("employment_rate = ?")
        query_values.append(employment_rate)

    # Add the employee ID to the query values
    query_values.append(employee_id)

    query = f"""
    UPDATE Employee
    SET {', '.join(query_parts)}, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    
    # Execute the query
    result = query_db(query, query_values, commit=True)

    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Employee updated successfully"}), 200


# DELETE an employee
@employee_bp.route('/backend/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    query = "DELETE FROM Employee WHERE id = ?"
    result = query_db(query, (employee_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Employee deleted successfully"}), 200
