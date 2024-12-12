import sqlite3
from datetime import datetime

DATABASE_NAME = "database.db"

def populate_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Populate the Person table
        cursor.executemany("""
            INSERT INTO Person (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, [
            ("Alice", "Smith", "1990-01-01", "123 Elm St", "555-1234", "alice.smith@example.com", "Online"),
            ("Bob", "Johnson", "1985-05-15", "456 Oak St", "555-5678", "bob.johnson@example.com", "Paper"),
            ("Carol", "Williams", "1975-07-20", "789 Maple St", "555-8765", "carol.williams@example.com", "Online"),
        ])

        # Get inserted person IDs for references
        alice_id = cursor.execute("SELECT id FROM Person WHERE first_name = 'Alice'").fetchone()[0]
        bob_id = cursor.execute("SELECT id FROM Person WHERE first_name = 'Bob'").fetchone()[0]
        carol_id = cursor.execute("SELECT id FROM Person WHERE first_name = 'Carol'").fetchone()[0]

        # Populate the Employee table
        cursor.executemany("""
            INSERT INTO Employee (person_id, role, employment_rate)
            VALUES (?, ?, ?);
        """, [
            (bob_id, "Technician", 80),
        ])

        # Populate the Tenant table
        cursor.executemany("""
            INSERT INTO Tenant (person_id, is_coroperative_member)
            VALUES (?, ?);
        """, [
            (alice_id, 1),
        ])

        # Get tenant IDs for references
        alice_tenant_id = cursor.execute("SELECT id FROM Tenant WHERE person_id = ?", (alice_id,)).fetchone()[0]

        # Populate the BoardMember table
        cursor.executemany("""
            INSERT INTO BoardMember (person_id, role)
            VALUES (?, ?);
        """, [
            (carol_id, "Secretary"),
        ])

        # Populate the Property table
        cursor.executemany("""
            INSERT INTO Property (name, address, property_document)
            VALUES (?, ?, ?);
        """, [
            ("Studentenhof", "Schülerstrasse 1-3, 9000 St.Gallen", None),
        ])

        # Get property IDs for references
        downtown_id = cursor.execute("SELECT id FROM Property WHERE name = 'Studentenhof'").fetchone()[0]

        # Populate the Unit table
        cursor.executemany("""
            INSERT INTO Unit (name, address, property_id)
            VALUES (?, ?, ?);
        """, [
            ("Studentenheim A", "Schülerstrasse 1, 9000 St.Gallen", downtown_id),
            ("Studentenheim B", "Schülerstrasse 2, 9000 St.Gallen", downtown_id),
        ])

        # Get unit IDs for references
        unit_a_id = cursor.execute("SELECT id FROM Unit WHERE name = 'Studentenheim A'").fetchone()[0]

        # Populate the Apartment table
        cursor.executemany("""
            INSERT INTO Apartment (size_sqm, rent, rooms, designation, unit_id)
            VALUES (?, ?, ?, ?, ?);
        """, [
            (50, 1200, 2, "Apartment A01", unit_a_id),
            (75, 1800, 3, "Apartment A02", unit_a_id),
            (35, 800, 1, "Apartment A03", unit_a_id),
        ])

        # Get apartment IDs for references
        apartment_101_id = cursor.execute("SELECT id FROM Apartment WHERE designation = 'Apartment A01'").fetchone()[0]

        # Populate the ParkingSpot table
        cursor.executemany("""
            INSERT INTO ParkingSpot (rent, spot_number, type, property_id)
            VALUES (?, ?, ?, ?);
        """, [
            (100, "P1", "Motorbike", downtown_id),
            (100, "P2", "Motorbike", downtown_id),
            (150, "P3", "Indoor", downtown_id),
            (150, "P4", "Indoor", downtown_id),
        ])

        # Get parking spot IDs for references
        parking_spot_p1_id = cursor.execute("SELECT id FROM ParkingSpot WHERE spot_number = 'P1'").fetchone()[0]
        parking_spot_p4_id = cursor.execute("SELECT id FROM ParkingSpot WHERE spot_number = 'P4'").fetchone()[0]

        # Populate the Contract table
        cursor.executemany("""
            INSERT INTO Contract (tenant_id, rental_type, rental_id, start_date, end_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?);
        """, [
            (alice_tenant_id, "Apartment", apartment_101_id, "2023-01-01", "2025-11-01", 0),
            (alice_tenant_id, "ParkingSpot", parking_spot_p1_id, "2023-02-01", "2025-11-01", 0),
            (alice_tenant_id, "ParkingSpot", parking_spot_p4_id, "2023-02-01", "2025-11-01", 0),
        ])


        # Insert a new vehicle
        cursor.execute("""
            INSERT INTO Vehicle (name, license_plate) 
            VALUES (?, ?);
        """, ("vw-pasat", "SG12345"))

        # Get the vehicle_id of the newly inserted vehicle
        result = cursor.execute("SELECT id FROM Vehicle WHERE name = ?", ("vw-pasat",)).fetchone()
        if result is None:
            raise ValueError("Vehicle 'vw-pasat' not found in the database.")
        vehicle_id = result[0]



        # # Insert three VehicleUsageLog entries
        # cursor.executemany("""
        #     INSERT INTO VehicleUsageLog (vehicle_id, employee_id, date_of_usage, purpose, distance_travelled) 
        #     VALUES (?, ?, ?, ?, ?);
        # """, [
        #     (vehicle_id, bob_id, datetime.now().strftime('%Y-%m-%d'), 'Delivery', 12.5),
        #     (vehicle_id, bob_id, datetime.now().strftime('%Y-%m-%d'), 'Repair', 8.0),
        #     (vehicle_id, bob_id, datetime.now().strftime('%Y-%m-%d'), 'Private', 25.3),
        # ])

        connection.commit()
        print("Database populated successfully!")

    except sqlite3.Error as e:
        print(f"An error occurred while populating the database: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    populate_database()
