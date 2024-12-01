import sqlite3

DATABASE_NAME = "database.db"

def populate_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:
        # Enable foreign key constraints and logging
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA foreign_key_check;")

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
        cursor.execute("""
            INSERT INTO Employee (person_id, role, employment_rate)
            VALUES (?, ?, ?);
        """, (alice_id, "Manager", 100))

        # Populate the Tenant table
        cursor.execute("""
            INSERT INTO Tenant (person_id, is_coroperative_member)
            VALUES (?, ?);
        """, (bob_id, 1))

        # Get tenant ID
        tenant_id = cursor.execute("SELECT id FROM Tenant WHERE person_id = ?", (bob_id,)).fetchone()[0]

        # Populate the BoardMember table
        cursor.execute("""
            INSERT INTO BoardMember (person_id, role)
            VALUES (?, ?);
        """, (carol_id, "President"))

        # Populate the Property table
        cursor.executemany("""
            INSERT INTO Property (name, address, property_document)
            VALUES (?, ?, ?);
        """, [
            ("Downtown Apartments", "123 City Center", None),
            ("Greenwood Complex", "456 Suburb Lane", None),
        ])

        # Get property IDs for references
        downtown_id = cursor.execute("SELECT id FROM Property WHERE name = 'Downtown Apartments'").fetchone()[0]

        # Populate the Unit table
        cursor.executemany("""
            INSERT INTO Unit (name, address, property_id)
            VALUES (?, ?, ?);
        """, [
            ("Unit A", "Unit A Address", downtown_id),
        ])

        # Get unit ID for references
        unit_a_id = cursor.execute("SELECT id FROM Unit WHERE name = 'Unit A'").fetchone()[0]

        # Populate the Apartment table
        cursor.execute("""
            INSERT INTO Apartment (size_sqm, rent, rooms, designation, unit_number, unit_id)
            VALUES (?, ?, ?, ?, ?, ?);
        """, ("50 sqm", 1200, 2, "Apartment 101", "101", unit_a_id))

        # Get apartment ID for references
        apartment_101_id = cursor.execute("SELECT id FROM Apartment WHERE designation = 'Apartment 101'").fetchone()[0]

        # Populate the ParkingSpot table
        cursor.execute("""
            INSERT INTO ParkingSpot (rent, spot_number, type, property_id)
            VALUES (?, ?, ?, ?);
        """, (100, "P1", "Motorbike", downtown_id))

        # Get parking spot ID for references
        parking_spot_p1_id = cursor.execute("SELECT id FROM ParkingSpot WHERE spot_number = 'P1'").fetchone()[0]

        # Populate the Contract table
        cursor.executemany("""
            INSERT INTO Contract (tenant_id, rental_type, rental_id, start_date, end_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?);
        """, [
            (tenant_id, "Apartment", apartment_101_id, "2023-01-01", "2024-01-01", 0),
            (tenant_id, "ParkingSpot", parking_spot_p1_id, "2023-01-01", "2024-01-01", 0),
        ])

        connection.commit()
        print("Database populated successfully!")

    except sqlite3.Error as e:
        print(f"An error occurred while populating the database: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    populate_database()
