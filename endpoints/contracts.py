from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime


# Define the Blueprint
contract_bp = Blueprint('contract', __name__)
DATABASE = 'database.db'

def query_db(query, args=(), one=False, commit=False, fetch_last_id=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            if fetch_last_id:
                return {"id": cursor.lastrowid}  # Return the last inserted row ID
            return {"status": "success"}
        else:
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
    except sqlite3.Error as e:
        return {"error": str(e)}
    finally:
        conn.close()




@contract_bp.route('/backend/contracts', methods=['POST'])
def create_contract():
    data = request.json

    # Tenant details
    tenant_id = data.get('tenant_id')
    is_cooperative_member = data.get('is_cooperative_member')

    # Person details (for creating a new tenant)
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')
    phone_number = data.get('phone_number')
    email = data.get('email')

    # Rental details
    rental_type = data.get('rental_type')
    rental_id = data.get('rental_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([rental_type, rental_id, start_date]):
        return jsonify({"error": "Rental type, rental ID, and start date are required"}), 400

    try:
        # If tenant_id is not provided, create a new tenant
        if not tenant_id:
            # Step 1: Create a new Person
            person_query = """
            INSERT INTO Person (first_name, last_name, date_of_birth, address, phone_number, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            person_result = query_db(
                person_query,
                (first_name, last_name, date_of_birth, address, phone_number, email),
                commit=True,
                fetch_last_id=True
            )

            if "error" in person_result:
                return jsonify(person_result), 500

            person_id = person_result.get("id")
            if not person_id:
                return jsonify({"error": "Failed to create Person, person_id not generated"}), 500

            # Step 2: Create a new Tenant linked to the Person
            tenant_query = """
            INSERT INTO Tenant (person_id, is_coroperative_member)
            VALUES (?, ?)
            """
            tenant_result = query_db(
                tenant_query,
                (person_id, is_cooperative_member),
                commit=True,
                fetch_last_id=True
            )

            if "error" in tenant_result:
                return jsonify(tenant_result), 500

            # Get the ID of the newly created tenant
            tenant_id = tenant_result["id"]

        # Validate rental type and associated IDs
        if rental_type == "Apartment":
            rental_check_query = "SELECT id FROM Apartment WHERE id = ?"
        elif rental_type == "ParkingSpot":
            rental_check_query = "SELECT id FROM ParkingSpot WHERE id = ?"
        else:
            return jsonify({"error": f"Invalid rental type: {rental_type}"}), 400

        # Validate rental existence
        rental_exists = query_db(rental_check_query, (rental_id,), one=True)
        if not rental_exists:
            return jsonify({"error": f"{rental_type} ID {rental_id} does not exist"}), 400

        # Validate end date
        if end_date and datetime.strptime(end_date, "%Y-%m-%d") < datetime.strptime(start_date, "%Y-%m-%d"):
            return jsonify({"error": "End date cannot be earlier than start date"}), 400

        # Step 3: Create the contract
        contract_query = """
        INSERT INTO Contract (tenant_id, rental_type, rental_id, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
        """
        contract_result = query_db(
            contract_query,
            (tenant_id, rental_type, rental_id, start_date, end_date),
            commit=True
        )

        if "error" in contract_result:
            return jsonify(contract_result), 500

        return jsonify({
            "message": "Contract created successfully",
            "contract": {
                "tenant_id": tenant_id,
                "rental_type": rental_type,
                "rental_id": rental_id,
                "start_date": start_date,
                "end_date": end_date
            }
        }), 201

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

    

# READ all contracts with person details
@contract_bp.route('/backend/contracts', methods=['GET'])
def get_contracts():
    rental_type = request.args.get('rental_type')  # Optional filter

    query = """
    SELECT
        Contract.id AS contract_id,
        Tenant.id AS tenant_id,
        Person.first_name || ' ' || Person.last_name AS tenant_name,
        Person.phone_number,
        Person.email,
        Contract.rental_type,
        Contract.rental_id,
        Contract.start_date,
        Contract.end_date,
        Contract.is_deleted
    FROM Contract
    JOIN Tenant ON Contract.tenant_id = Tenant.id
    JOIN Person ON Tenant.person_id = Person.id
    WHERE Contract.is_deleted = 0
    """
    
    params = []
    if rental_type:
        query += " AND Contract.rental_type = ?"
        params.append(rental_type)

    query += " ORDER BY Tenant.id, Contract.start_date DESC"

    result = query_db(query, params)
    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 500

    return jsonify(result), 200



    

#update the end date of a contract
@contract_bp.route('/backend/contracts/<int:contract_id>', methods=['PUT'])
def update_contract(contract_id):
    data = request.json
    end_date = data.get('end_date')

    if not end_date:
        return jsonify({"error": "end_date is required"}), 400

    query = """
    UPDATE Contract
    SET end_date = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ? AND is_deleted = 0
    """
    result = query_db(query, (end_date, contract_id), commit=True)

    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Contract updated successfully"}), 200



# Soft DELETE a contract
@contract_bp.route('/backend/contracts/<int:contract_id>', methods=['DELETE'])
def soft_delete_contract(contract_id):
    query = """
    UPDATE Contract
    SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (contract_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Contract soft-deleted successfully"}), 200