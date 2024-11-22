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


@contract_bp.route('/backend/contracts', methods=['POST'])
def create_contract():
    data = request.json

    # Tenant details
    tenant_id = data.get('tenant_id')
    is_cooperative_member = data.get('is_cooperative_member')

    # Rental details
    rental_type = data.get('rental_type')
    rental_id = data.get('rental_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    # Optional details
    apartment_id = data.get('apartment_id')  # Only for Apartment rental type
    parking_id = data.get('parking_id')      # Only for ParkingSpot rental type
    unit_id = data.get('unit_id')            # Only for Apartment rentals

    
    if not all([rental_type, start_date]):
        return jsonify({"error": "Rental type and start date are required"}), 400


    try:
        # If tenant_id is not provided, create a new tenant
        if not tenant_id:
            tenant_query = """
            INSERT INTO Tenant (is_coroperative_member, apartment_id, parking_id)
            VALUES (?, ?, ?)
            """
            tenant_result = query_db(
                tenant_query,
                (is_cooperative_member, apartment_id if rental_type == "Apartment" else None, 
                parking_id if rental_type == "ParkingSpot" else None),
                commit=True
            )

            if "error" in tenant_result:
                return jsonify(tenant_result), 500

            # Get the ID of the newly created tenant
            tenant_id_query = "SELECT last_insert_rowid() AS tenant_id"
            tenant_id_result = query_db(tenant_id_query, one=True)
            tenant_id = tenant_id_result['tenant_id']

        # Validate rental type and associated IDs
        rental_id = None  # Initialize rental_id

        if rental_type == "Apartment":
            if not apartment_id:
                return jsonify({"error": "Apartment ID is required for Apartment rental type"}), 400

            # Validate apartment existence
            apartment_check_query = "SELECT id FROM Apartment WHERE id = ?"
            apartment_exists = query_db(apartment_check_query, (apartment_id,), one=True)
            if not apartment_exists:
                return jsonify({"error": f"Apartment ID {apartment_id} does not exist"}), 400

            # Set rental_id to the apartment_id
            rental_id = apartment_id

            # Validate unit_id if provided
            if unit_id:
                unit_check_query = "SELECT id FROM Unit WHERE id = ?"
                unit_exists = query_db(unit_check_query, (unit_id,), one=True)
                if not unit_exists:
                    return jsonify({"error": f"Unit ID {unit_id} does not exist"}), 400

        elif rental_type == "ParkingSpot":
            if not parking_id:
                return jsonify({"error": "Parking Spot ID is required for ParkingSpot rental type"}), 400

            # Validate parking spot existence
            parking_check_query = "SELECT id FROM ParkingSpot WHERE id = ?"
            parking_exists = query_db(parking_check_query, (parking_id,), one=True)
            if not parking_exists:
                return jsonify({"error": f"Parking Spot ID {parking_id} does not exist"}), 400

            # Set rental_id to the parking_id
            rental_id = parking_id

        # Ensure rental_id is set
        if rental_id is None:
            return jsonify({"error": "Could not determine rental ID for the contract"}), 400

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
        print(f"Error occurred: {e}")
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