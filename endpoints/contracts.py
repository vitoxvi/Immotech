from flask import Blueprint, request, jsonify
import sqlite3


# Define the Blueprint
contract_bp = Blueprint('contract', __name__)
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


# CREATE a new contract
@contract_bp.route('/backend/contracts', methods=['POST'])
def create_contract():
    data = request.json

    # Tenant details
    tenant_id = data.get('tenant_id')
    is_cooperative_member = data.get('is_cooperative_member')
    apartment_id = data.get('apartment_id')
    parking_id = data.get('parking_id')

    # Contract details
    rental_type = data.get('rental_type')
    rental_id = data.get('rental_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([rental_type, rental_id, start_date]):
        return jsonify({"error": "Rental type, rental ID, and start date are required"}), 400

    try:
        # If tenant_id is not provided, create a new tenant
        if not tenant_id:
            tenant_query = """
            INSERT INTO Tenant (is_coroperative_member, apartment_id, parking_id)
            VALUES (?, ?, ?)
            """
            tenant_result = query_db(
                tenant_query,
                (is_cooperative_member, apartment_id, parking_id),
                commit=True
            )
            if "error" in tenant_result:
                return jsonify(tenant_result), 500

            # Get the ID of the newly created tenant
            tenant_id_query = "SELECT last_insert_rowid() AS tenant_id"
            tenant_id_result = query_db(tenant_id_query, one=True)
            tenant_id = tenant_id_result['tenant_id']

        # Create the contract
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

        return jsonify({"message": "Contract created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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