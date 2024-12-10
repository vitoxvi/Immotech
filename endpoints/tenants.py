from flask import Blueprint, request, jsonify
import sqlite3

tenant_bp = Blueprint('tenant', __name__)
DATABASE = 'database.db'

# Helper function for database operations
def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
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


@tenant_bp.route('/backend/tenants', methods=['GET'])
def get_tenants():
    property_id = request.args.get('property_id')
    unit_id = request.args.get('unit_id')
    rental_type = request.args.get('rental_type')  # New filter for rental type

    # Base query
    query = """
    SELECT
        Tenant.id AS tenant_id,
        Tenant.is_coroperative_member,
        Person.first_name,
        Person.last_name,
        Person.date_of_birth,
        Person.address,
        Person.phone_number,
        Person.email,
        Contract.rental_type,
        Contract.start_date,
        Contract.end_date,
        CASE
            WHEN Contract.rental_type = 'Apartment' THEN Apartment.unit_id
            ELSE NULL
        END AS unit_id
    FROM Tenant
    JOIN Person ON Tenant.person_id = Person.id
    JOIN Contract ON Tenant.id = Contract.tenant_id
    LEFT JOIN Apartment ON Contract.rental_type = 'Apartment' AND Contract.rental_id = Apartment.id
    LEFT JOIN ParkingSpot ON Contract.rental_type = 'ParkingSpot' AND Contract.rental_id = ParkingSpot.id
    WHERE (Contract.end_date IS NULL OR Contract.end_date >= DATE('now')) AND Contract.is_deleted = 0

    """

    # Filtering logic
    filters = []
    params = []

    if rental_type:
        filters.append("Contract.rental_type = ?")
        params.append(rental_type)

    if property_id:
        filters.append("""
            (Apartment.unit_id IN (SELECT id FROM Unit WHERE property_id = ?)
            OR ParkingSpot.property_id = ?)
        """)
        params.extend([property_id, property_id])

    if unit_id:
        filters.append("Apartment.unit_id = ?")
        params.append(unit_id)

    if filters:
        query += " AND " + " AND ".join(filters)

    result = query_db(query, params)
    if "error" in result:
        return jsonify(result), 500

    tenants = [dict(row) for row in result]
    return jsonify(tenants), 200



# Update tenant
@tenant_bp.route('/backend/tenants/<int:tenant_id>', methods=['PUT'])
def update_tenant(tenant_id):
    data = request.json
    is_cooperative_member = data.get('is_cooperative_member')

    # Update query
    query = """
    UPDATE Tenant
    SET is_coroperative_member = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """
    result = query_db(query, (is_cooperative_member, tenant_id), commit=True)

    if "error" in result:
        return jsonify(result), 500

    return jsonify({"message": "Tenant updated successfully"}), 200

