import sqlite3

DATABASE = 'database.db'

def populate_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Insert sample data into Person table
        cursor.executescript('''
        INSERT INTO Person (first_name, last_name, date_of_birth, address, phone_number, email, bank_correspondence)
        VALUES 
        ('Hans', 'Müller', '1980-03-15', 'Bahnhofstrasse 1, 8001 Zürich', '+41 44 123 4567', 'hans.mueller@example.com', 'UBS'),
        ('Anna', 'Meier', '1992-06-21', 'Marktgasse 10, 9000 St. Gallen', '+41 71 234 5678', 'anna.meier@example.com', 'Credit Suisse'),
        ('Peter', 'Schneider', '1975-12-03', 'Rue de Bourg 5, 1003 Lausanne', '+41 21 345 6789', 'peter.schneider@example.com', 'Raiffeisen'),
        ('Clara', 'Fischer', '1988-09-12', 'Steinentorstrasse 20, 4051 Basel', '+41 61 456 7890', 'clara.fischer@example.com', 'ZKB'),
        ('Luca', 'Keller', '2000-01-28', 'Langstrasse 50, 8004 Zürich', '+41 44 567 8901', 'luca.keller@example.com', 'PostFinance');

        -- Insert sample data into Employee table
        INSERT INTO Employee (id, role, employment_rate)
        VALUES 
        (1, 'Manager', 100),
        (2, 'Technician', 80),
        (3, 'Cleaner', 60);

        -- Insert sample data into Unit table
        INSERT INTO Unit (name, address, property_id)
        VALUES
        ('Unit A', 'Bahnhofstrasse 1, 8001 Zürich', 1),
        ('Unit B', 'Seestrasse 100, 8700 Küsnacht', 2);

        -- Insert sample data into Tenant table
        INSERT INTO Tenant (id, is_coroperative_member, apartment_id, parking_id)
        VALUES 
        (4, 1, 1, NULL),
        (5, 0, 2, 1);

        -- Insert sample data into BoardMember table
        INSERT INTO BoardMember (id, role)
        VALUES 
        (1, 'President'),
        (2, 'Treasurer');

        -- Insert sample data into Vehicle table
        INSERT INTO Vehicle (name, license_plate)
        VALUES 
        ('Mercedes Vito', 'ZH 123456'),
        ('BMW X5', 'SG 654321');

        -- Insert sample data into VehicleUsageLog table
        INSERT INTO VehicleUsageLog (vehicle_id, employee_id, date_of_usage, purpose, distance_travelled)
        VALUES 
        (1, 2, '2024-11-01', 'Repair', 50),
        (2, 1, '2024-11-05', 'Delivery', 120);

        -- Insert sample data into Property table
        INSERT INTO Property (name, address)
        VALUES 
        ('City Center Building', 'Bahnhofstrasse 1, 8001 Zürich'),
        ('Lakeside Apartments', 'Seestrasse 100, 8700 Küsnacht');

        -- Insert sample data into Apartment table
        INSERT INTO Apartment (size_sqm, rent, rooms, designation, unit_number, unit_id)
        VALUES 
        ('85', 2200, 3, 'Premium', '1A', 1),
        ('120', 3500, 4, 'Luxury', '2B', 2);

        -- Insert sample data into ParkingSpot table
        INSERT INTO ParkingSpot (rent, spot_number, type, property_id)
        VALUES 
        (150, 'P1', 'Indoor', 1),
        (200, 'P2', 'ElectricCar', 2);

        -- Insert sample data into Contract table
        INSERT INTO Contract (tenant_id, rental_type, rental_id, start_date, end_date)
        VALUES 
        (4, 'Apartment', 1, '2023-01-01', '2024-12-31'),
        (5, 'Apartment', 2, '2023-05-01', NULL),
        (5, 'ParkingSpot', 1, '2023-06-01', NULL);
        ''')
        
        conn.commit()
        print("Mock data successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    populate_database()
