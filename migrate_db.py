import sqlite3
import os

# Get the database file path
db_path = os.path.join(os.path.dirname(__file__), 'database', 'trashway.db')

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns exist and add them if not
try:
    # Try to select one row to see what columns exist
    cursor.execute("SELECT * FROM bins LIMIT 1")
    columns = [description[0] for description in cursor.description]
    
    # Check and add missing columns
    if "street_number" not in columns:
        print("Adding street_number column")
        cursor.execute("ALTER TABLE bins ADD COLUMN street_number TEXT DEFAULT '1'")
    
    if "street_name" not in columns:
        print("Adding street_name column")
        cursor.execute("ALTER TABLE bins ADD COLUMN street_name TEXT DEFAULT 'Rue de Paris'")
    
    if "postal_code" not in columns:
        print("Adding postal_code column")
        cursor.execute("ALTER TABLE bins ADD COLUMN postal_code TEXT DEFAULT '75000'")
    
    if "city" not in columns:
        print("Adding city column")
        cursor.execute("ALTER TABLE bins ADD COLUMN city TEXT DEFAULT 'Paris'")
    
    if "country" not in columns:
        print("Adding country column")
        cursor.execute("ALTER TABLE bins ADD COLUMN country TEXT DEFAULT 'France'")
    
    # Commit changes
    conn.commit()
    print("Database migration completed successfully")
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    conn.close()
