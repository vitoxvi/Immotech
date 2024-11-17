from flask import Blueprint, request, jsonify
import sqlite3

# Define the Blueprint
tenant_bp = Blueprint('tenant', __name__)
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


# CREATE a new tenant
@tenant_bp.route('/tenants', methods=['POST'])
def create_tenant():
    data = request.json
    id = data.get('id')
    is_cooperative_member = data.get('is_cooperative_member')
    apartment_id = data.get('apartment_id')
    parking_id = data.get('parking_id')

    if id is None or is_cooperative_member is None:
        return jsonify({"error": "Tenant ID and cooperative membership status are required"}), 400

    query = """
    INSERT INTO Tenant (id, is_coroperative_member, apartment_id, parking_id)
    VALUES (?, ?, ?, ?)
    """
    result = query_db(query, (id, is_cooperative_member, apartment_id, parking_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Tenant created successfully"}), 201


# READ all tenants
@tenant_bp.route('/tenants', methods=['GET'])
def get_all_tenants():
    query = "SELECT * FROM Tenant"
    result = query_db(query)
    if "error" in result:
        return jsonify(result), 500

    tenants = [dict(row) for row in result]
    return jsonify(tenants), 200


# READ a single tenant by ID
@tenant_bp.route('/tenants/<int:tenant_id>', methods=['GET'])
def get_tenant(tenant_id):
    query = "SELECT * FROM Tenant WHERE id = ?"
    result = query_db(query, (tenant_id,), one=True)
    if not result:
        return jsonify({"error": "Tenant not found"}), 404

    return jsonify(dict(result)), 200


# UPDATE an existing tenant
@tenant_bp.route('/tenants/<int:tenant_id>', methods=['PUT'])
def update_tenant(tenant_id):
    data = request.json
    is_cooperative_member = data.get('is_cooperative_member')
    apartment_id = data.get('apartment_id')
    parking_id = data.get('parking_id')

    if is_cooperative_member is None:
        return jsonify({"error": "Cooperative membership status is required"}), 400

    query = """
    UPDATE Tenant
    SET is_coroperative_member = ?, apartment_id = ?, parking_id = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (is_cooperative_member, apartment_id, parking_id, tenant_id), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Tenant updated successfully"}), 200


# DELETE a tenant
@tenant_bp.route('/tenants/<int:tenant_id>', methods=['DELETE'])
def delete_tenant(tenant_id):
    query = "DELETE FROM Tenant WHERE id = ?"
    result = query_db(query, (tenant_id,), commit=True)
    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Tenant deleted successfully"}), 200
