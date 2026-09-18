import sqlite3
from pathlib import Path

# Store the database inside the project data directory
DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "housing.db"


def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)


def initialise_database():
    """Create the properties table if it does not already exist."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suburb TEXT NOT NULL,
            land_size REAL NOT NULL,
            contract_year INTEGER NOT NULL,
            contract_month INTEGER NOT NULL,
            zoning TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def create_property(suburb, land_size, contract_year, contract_month, zoning):
    """Create a new property record."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO properties
        (suburb, land_size, contract_year, contract_month, zoning)
        VALUES (?, ?, ?, ?, ?)
    """, (
        suburb,
        land_size,
        contract_year,
        contract_month,
        zoning
    ))

    property_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return property_id


def get_all_properties():
    """Read and return all property records."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, suburb, land_size, contract_year,
               contract_month, zoning, created_at
        FROM properties
        ORDER BY id DESC
    """)

    properties = cursor.fetchall()

    connection.close()

    return properties


def get_property(property_id):
    """Read a single property by ID."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, suburb, land_size, contract_year,
               contract_month, zoning, created_at
        FROM properties
        WHERE id = ?
    """, (property_id,))

    property_record = cursor.fetchone()

    connection.close()

    return property_record


def update_property(
    property_id,
    suburb,
    land_size,
    contract_year,
    contract_month,
    zoning
):
    """Update an existing property record."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE properties
        SET suburb = ?,
            land_size = ?,
            contract_year = ?,
            contract_month = ?,
            zoning = ?
        WHERE id = ?
    """, (
        suburb,
        land_size,
        contract_year,
        contract_month,
        zoning,
        property_id
    ))

    rows_updated = cursor.rowcount

    connection.commit()
    connection.close()

    return rows_updated


def delete_property(property_id):
    """Delete a property record by ID."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM properties
        WHERE id = ?
    """, (property_id,))

    rows_deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return rows_deleted


if __name__ == "__main__":
    initialise_database()
    print(f"Database initialised successfully: {DATABASE_PATH}")