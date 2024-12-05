import sqlite3

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
            (alice_id, "Manager", 100),
            (bob_id, "Technician", 80),
            (carol_id, "Cleaner", 50),
        ])

        # Populate the Tenant table
        cursor.executemany("""
            INSERT INTO Tenant (person_id, is_coroperative_member)
            VALUES (?, ?);
        """, [
            (alice_id, 1),
            (bob_id, 0),
            (carol_id, 1),
        ])

        # Get tenant IDs for references
        alice_tenant_id = cursor.execute("SELECT id FROM Tenant WHERE person_id = ?", (alice_id,)).fetchone()[0]
        bob_tenant_id = cursor.execute("SELECT id FROM Tenant WHERE person_id = ?", (bob_id,)).fetchone()[0]

        # Populate the BoardMember table
        cursor.executemany("""
            INSERT INTO BoardMember (person_id, role)
            VALUES (?, ?);
        """, [
            (alice_id, "President"),
            (bob_id, "Treasurer"),
            (carol_id, "Secretary"),
        ])

        # Populate the Property table
        cursor.executemany("""
            INSERT INTO Property (name, address, property_document)
            VALUES (?, ?, ?);
        """, [
            ("Downtown Apartments", "123 City Center", None),
            ("Greenwood Complex", "456 Suburb Lane", None),
            ("Skyline Towers", "789 Metro Blvd", None),
        ])

        # Get property IDs for references
        downtown_id = cursor.execute("SELECT id FROM Property WHERE name = 'Downtown Apartments'").fetchone()[0]
        greenwood_id = cursor.execute("SELECT id FROM Property WHERE name = 'Greenwood Complex'").fetchone()[0]

        # Populate the Unit table
        cursor.executemany("""
            INSERT INTO Unit (name, address, property_id)
            VALUES (?, ?, ?);
        """, [
            ("Unit A", "123 City Center - Unit A", downtown_id),
            ("Unit B", "123 City Center - Unit B", downtown_id),
            ("Unit C", "456 Suburb Lane - Unit C", greenwood_id),
        ])

        # Get unit IDs for references
        unit_a_id = cursor.execute("SELECT id FROM Unit WHERE name = 'Unit A'").fetchone()[0]

        # Populate the Apartment table
        cursor.executemany("""
            INSERT INTO Apartment (size_sqm, rent, rooms, designation, unit_id)
            VALUES (?, ?, ?, ?, ?);
        """, [
            ("50 sqm", 1200, 2, "Apartment 101", unit_a_id),
            ("75 sqm", 1800, 3, "Apartment 102", unit_a_id),
            ("35 sqm", 800, 1, "Apartment 103", unit_a_id),
        ])

        # Get apartment IDs for references
        apartment_101_id = cursor.execute("SELECT id FROM Apartment WHERE designation = 'Apartment 101'").fetchone()[0]
        apartment_102_id = cursor.execute("SELECT id FROM Apartment WHERE designation = 'Apartment 102'").fetchone()[0]

        # Populate the ParkingSpot table
        cursor.executemany("""
            INSERT INTO ParkingSpot (rent, spot_number, type, property_id)
            VALUES (?, ?, ?, ?);
        """, [
            (100, "P1", "Motorbike", downtown_id),
            (150, "P2", "Indoor", downtown_id),
            (50, "P3", "Outdoor", greenwood_id),
        ])

        # Get parking spot IDs for references
        parking_spot_p1_id = cursor.execute("SELECT id FROM ParkingSpot WHERE spot_number = 'P1'").fetchone()[0]

        # Populate the Contract table
        cursor.executemany("""
            INSERT INTO Contract (tenant_id, rental_type, rental_id, start_date, end_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?);
        """, [
            (alice_tenant_id, "Apartment", apartment_101_id, "2023-01-01", "2024-01-01", 0),
            (alice_tenant_id, "Apartment", apartment_102_id, "2023-02-01", None, 0),
            (bob_tenant_id, "ParkingSpot", parking_spot_p1_id, "2023-03-01", "2024-03-01", 0),
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
