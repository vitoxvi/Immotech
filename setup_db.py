import sqlite3

# Database file name
DATABASE_NAME = "database.db"

# SQL schema definition with triggers
SQL_SCHEMA = """
PRAGMA foreign_keys = ON;

-- Table definitions (unchanged)
CREATE TABLE IF NOT EXISTS Person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT,
    address TEXT,
    phone_number TEXT,
    email TEXT,
    bank_correspondence TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_last_name_first_name ON Person (last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_email ON Person (email);

CREATE TABLE IF NOT EXISTS Employee (
    id INTEGER PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('Manager', 'Technician', 'Cleaner', 'Administrator', 'Accountant', 'Other')),
    employment_rate REAL NOT NULL CHECK (employment_rate > 0 AND employment_rate <= 100),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Tenant (
    id INTEGER PRIMARY KEY,
    is_coroperative_member INTEGER NOT NULL CHECK (is_coroperative_member IN (0, 1)),
    apartment_id INTEGER,
    parking_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (apartment_id) REFERENCES Apartment (id) ON DELETE SET NULL,
    FOREIGN KEY (parking_id) REFERENCES ParkingSpot (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_apartment_id ON Tenant (apartment_id);
CREATE INDEX IF NOT EXISTS idx_parking_id ON Tenant (parking_id);

CREATE TABLE IF NOT EXISTS BoardMember (
    id INTEGER PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('President', 'Vice-president', 'Secretary', 'Treasurer', 'Member')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS VehicleUsageLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    date_of_usage TEXT NOT NULL,
    purpose TEXT DEFAULT 'Other' CHECK (purpose IN ('Delivery', 'Repair', 'Inspection', 'Private', 'Other')),
    distance_travelled REAL CHECK (distance_travelled >= 0),
    is_deleted INTEGER DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle (id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES Employee (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_vehicle_id ON VehicleUsageLog (vehicle_id);
CREATE INDEX IF NOT EXISTS idx_employee_id ON VehicleUsageLog (employee_id);
CREATE INDEX IF NOT EXISTS idx_date_of_usage ON VehicleUsageLog (date_of_usage);

CREATE TABLE IF NOT EXISTS Vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    license_plate TEXT,
    vehicle_document BLOB,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_license_plate ON Vehicle (license_plate);

CREATE TABLE IF NOT EXISTS Property (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    property_document BLOB,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_address ON Property (address);


CREATE TABLE IF NOT EXISTS Unit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    property_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES Property (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_property_id ON Unit (property_id);

CREATE TABLE IF NOT EXISTS Apartment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    size_sqm TEXT NOT NULL,
    rent REAL NOT NULL CHECK (rent >= 0),
    rooms INTEGER CHECK (rooms >= 0),
    designation TEXT,
    unit_number TEXT NOT NULL,
    unit_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES Unit (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_unit_id ON Apartment (unit_id);
CREATE INDEX IF NOT EXISTS idx_rent ON Apartment (rent);
CREATE INDEX IF NOT EXISTS idx_rooms ON Apartment (rooms);


CREATE TABLE IF NOT EXISTS ParkingSpot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rent REAL NOT NULL CHECK (rent >= 0),
    spot_number TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('Motorbike', 'ElectricCar', 'Indoor', 'Outdoor')),
    property_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES Property (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_property_id ON ParkingSpot (property_id);
CREATE INDEX IF NOT EXISTS idx_type ON ParkingSpot (type);

CREATE TABLE IF NOT EXISTS Contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    rental_type TEXT NOT NULL CHECK (rental_type IN ('Apartment', 'ParkingSpot')),
    rental_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT CHECK (end_date >= start_date),
    is_deleted INTEGER DEFAULT 0 CHECK (is_deleted IN (0, 1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES Tenant (id) ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_tenant_id ON Contract (tenant_id);
CREATE INDEX IF NOT EXISTS idx_rental_id ON Contract (rental_id);
CREATE INDEX IF NOT EXISTS idx_start_date_end_date ON Contract (start_date, end_date);

-- Triggers to update the updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_person_timestamp
AFTER UPDATE ON Person
FOR EACH ROW
BEGIN
  UPDATE Person SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_employee_timestamp
AFTER UPDATE ON Employee
FOR EACH ROW
BEGIN
  UPDATE Employee SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_tenant_timestamp
AFTER UPDATE ON Tenant
FOR EACH ROW
BEGIN
  UPDATE Tenant SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_boardmember_timestamp
AFTER UPDATE ON BoardMember
FOR EACH ROW
BEGIN
  UPDATE BoardMember SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_vehicleusagelog_timestamp
AFTER UPDATE ON VehicleUsageLog
FOR EACH ROW
BEGIN
  UPDATE VehicleUsageLog SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_vehicle_timestamp
AFTER UPDATE ON Vehicle
FOR EACH ROW
BEGIN
  UPDATE Vehicle SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_property_timestamp
AFTER UPDATE ON Property
FOR EACH ROW
BEGIN
  UPDATE Property SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_apartment_timestamp
AFTER UPDATE ON Apartment
FOR EACH ROW
BEGIN
  UPDATE Apartment SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_parkingspot_timestamp
AFTER UPDATE ON ParkingSpot
FOR EACH ROW
BEGIN
  UPDATE ParkingSpot SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_contract_timestamp
AFTER UPDATE ON Contract
FOR EACH ROW
BEGIN
  UPDATE Contract SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
"""

# Function to set up the database
def setup_database():
    # Connect to the SQLite database
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    try:       
        # Drop all existing tables
        cursor.executescript("""
        PRAGMA foreign_keys = OFF;
        DROP TABLE IF EXISTS VehicleUsageLog;
        DROP TABLE IF EXISTS Vehicle;
        DROP TABLE IF EXISTS Employee;
        DROP TABLE IF EXISTS Person;
        DROP TABLE IF EXISTS Tenant;
        DROP TABLE IF EXISTS BoardMember;
        DROP TABLE IF EXISTS Property;
        DROP TABLE IF EXISTS Apartment;
        DROP TABLE IF EXISTS ParkingSpot;
        DROP TABLE IF EXISTS Contract;
        PRAGMA foreign_keys = ON;
        """)
        print("All existing tables dropped successfully.")

        # Execute the schema to recreate the tables
        cursor.executescript(SQL_SCHEMA)
        print(f"Database setup completed successfully: {DATABASE_NAME}")
    except sqlite3.Error as e:
        print(f"An error occurred while setting up the database: {e}")
    finally:
        # Close the connection
        connection.commit()
        connection.close()

# Run the setup
if __name__ == "__main__":
    setup_database()
