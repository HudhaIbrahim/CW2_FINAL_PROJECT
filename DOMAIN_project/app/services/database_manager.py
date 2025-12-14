from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.db import DATA_DIR, DB_PATH
import pandas as pd
from pathlib import Path

class DatabaseManager:
    """Database management service."""
    def __init__(self):
        self.conn = connect_database()

    # MIGRATE USERS FROM FILE
    def migrate_users_from_file(conn, filename="users.txt"):
        """
        Migrate users from DATA/users.txt into the users table.
        Expected file format:
            username,password_hash,role
        """
        users_file = DATA_DIR / filename

        if not users_file.exists():
            print(f"⚠️ File not found: {users_file}")
            print("No users migrated.")
            return 0

        cursor = conn.cursor()
        migrated = 0

        with open(users_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                try:
                    username, password_hash, role = line.split(",")

                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO users (username, password_hash, role)
                        VALUES (?, ?, ?)
                        """,
                        (username.strip(), password_hash.strip(), role.strip())
                    )

                    if cursor.rowcount > 0:
                        migrated += 1

                except Exception as e:
                    print(f"Error processing line '{line}': {e}")

        conn.commit()
        print(f"✅ Migrated {migrated} users from {users_file}")
        return migrated

    # LOAD CSV INTO TABLE
    def load_csv_to_table(conn, csv_path, table_name):

        if not Path(csv_path).exists():
            print(f"File not found: {csv_path}")
            return False

        df = pd.read_csv(csv_path)
        df.to_sql(table_name, con=conn, if_exists="append", index=False)
        print(f"✅ Loaded {len(df)} rows from {csv_path} into table '{table_name}'.")
        return len(df)


    def load_all_csv_data(conn):
        csv_map = {
            "cyber-operations-incidents.csv": "cyber_incidents",
            "datasets_metadata.csv": "datasets_metadata",
            "it_tickets.csv": "it_tickets"
        }

        total_rows = 0

        for file, table in csv_map.items():
            csv_path = DATA_DIR / file
            rows = DatabaseManager.load_csv_to_table(conn, csv_path, table)
            total_rows += rows if rows else 0

        return total_rows


def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "="*60)
    print("STARTING COMPLETE DATABASE SETUP")
    print("="*60)
    
    # Step 1: Connect
    print("\n[1/5] Connecting to database...")
    conn = connect_database()
    print("       Connected")
    
    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    create_all_tables(conn)
    
    # Step 3: Migrate users
    print("\n[3/5] Migrating users from users.txt...")
    user_count = DatabaseManager.migrate_users_from_file(conn)
    print(f"Migrated {user_count} users")
    
    # Step 4: Load CSV data
    print("\n[4/5] Loading CSV data...")
    total_rows = DatabaseManager.load_all_csv_data(conn)
    
    # Step 5: Verify
    print("\n[5/5] Verifying database setup...")
    cursor = conn.cursor()
    
    # Count rows in each table
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n Database Summary:")
    print(f"{'Table':<25} {'Row Count':<15}")
    print("-" * 40)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} {count:<15}")
    
    conn.close()
    
    print("\n" + "="*60)
    print(" DATABASE SETUP COMPLETE!")
    print("="*60)
    print(f"\n Database location: {DB_PATH.resolve()}")

    # Run the complete setup
    setup_database_complete()