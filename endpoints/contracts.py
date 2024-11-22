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
@contract_bp.route('/contracts', methods=['POST'])
def create_contract():
    data = request.json
    tenant_id = data.get('tenant_id')
    rental_type = data.get('rental_type')
    rental_id = data.get('rental_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([tenant_id, rental_type, rental_id, start_date]):
        return jsonify({"error": "All required fields must be provided"}), 400

    query = """
    INSERT INTO Contract (tenant_id, rental_type, rental_id, start_date, end_date)
    VALUES (?, ?, ?, ?, ?)
    """
    result = query_db(query, (tenant_id, rental_type, rental_id, start_date, end_date), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Contract created successfully"}), 201


# READ all contracts
@contract_bp.route('/contracts', methods=['GET'])
def get_all_contracts():
    query = "SELECT * FROM Contract"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    contracts = [dict(row) for row in result]
    return jsonify(contracts), 200


# READ a single contract by ID
@contract_bp.route('/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    query = "SELECT * FROM Contract WHERE id = ?"
    result = query_db(query, (contract_id,), one=True)
    if not result:
        return jsonify({"error": "Contract not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing contract
@contract_bp.route('/contracts/<int:contract_id>', methods=['PUT'])
def update_contract(contract_id):
    data = request.json
    tenant_id = data.get('tenant_id')
    rental_type = data.get('rental_type')
    rental_id = data.get('rental_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([tenant_id, rental_type, rental_id, start_date]):
        return jsonify({"error": "All required fields must be provided"}), 400

    query = """
    UPDATE Contract
    SET tenant_id = ?, rental_type = ?, rental_id = ?, start_date = ?, end_date = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (tenant_id, rental_type, rental_id, start_date, end_date, contract_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Contract updated successfully"}), 200


# Soft DELETE a contract
@contract_bp.route('backend/contracts/<int:contract_id>', methods=['DELETE'])
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