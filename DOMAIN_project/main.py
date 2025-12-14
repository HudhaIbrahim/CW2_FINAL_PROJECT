from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.auth_manager import register_user, login_user
from app.services.database_manager import DatabaseManager
from app.data.incidents import Incident

def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)
    
    # 1. Setup database
    conn = connect_database()
    create_all_tables(conn)

    
    # 2. Migrate users
    DatabaseManager.migrate_users_from_file(conn)

    # Load CSV data
    DatabaseManager.load_all_csv_data(conn)
    
    # 3. Test authentication
    success, msg = register_user("alice", "SecurePass123!", "analyst")
    print(msg)
    
    success, msg = login_user("alice", "SecurePass123!")
    print(msg)

    # 4. Test CRUD
    new_incident = Incident(
        date="2024-11-05",
        incident_type="phishing",
        severity="high",
        status="open",
        description="suspicious email detected",
        reported_by="Alice"
    )
    incident_id = new_incident.insert_incident()
    print(f"Created incident #{incident_id}")

    
    # 5. Query data
    df = Incident.get_all_incidents()
    print(f"Total incidents: {len(df)}")

    # Test: Run analytical queries

    print("\n Incidents by Type:")
    df_by_type = Incident.get_incidents_by_type_count(conn)
    print(df_by_type)

    print("\n High Severity Incidents by Status:")
    df_high_severity = Incident.get_high_severity_by_status(conn)
    print(df_high_severity)

    print("\n Incident Types with Many Cases (>5):")
    df_many_cases = Incident.get_incident_types_with_many_cases(conn, min_count=5)
    print(df_many_cases)

    conn.close()

if __name__ == "__main__":
    main()