import pandas as pd
from app.data.db import connect_database

class Incident:
    """Class representing a cyber incident."""

    def __init__(self, id=None, date=None, incident_type=None, severity=None, status=None, description=None, reported_by=None):
        self.id = id
        self.date = date
        self.incident_type = incident_type
        self.severity = severity
        self.status = status
        self.description = description
        self.reported_by = reported_by

    def __str__(self):
        return f"Incident(id={self.id}, date={self.date}, type={self.incident_type}, severity={self.severity}, status={self.status}, reported_by={self.reported_by})"

# CRUD Methods

    def insert_incident(self):
        """Insert new incident."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cyber_incidents 
            (date, incident_type, severity, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.date, self.incident_type, self.severity, self.status, self.description, self.reported_by))
        conn.commit()
        incident_id = cursor.lastrowid # Get the ID of the inserted incident
        conn.close()
        return incident_id

    @staticmethod
    def get_all_incidents():
        """Get all incidents as DataFrame."""
        conn = connect_database()
        df = pd.read_sql_query(
            "SELECT * FROM cyber_incidents ORDER BY id DESC",
            conn
        )
        conn.close()
        return df

    @staticmethod
    def update_incident_status(incident_id, new_status):
        """Update the status of an incident."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cyber_incidents
            SET status = ?
            WHERE id = ?
        """, (new_status, incident_id))
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        return affected_rows

    @staticmethod
    def delete_incident(incident_id):
        """Delete an incident by ID."""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM cyber_incidents
            WHERE id = ?
        """, (incident_id,))
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        return affected_rows

    # Analytics Methods
    @staticmethod
    def get_incidents_by_type_count(conn):
        """
        Count incidents by type.
        Uses: SELECT, FROM, GROUP BY, ORDER BY
        """
        query = """
        SELECT incident_type, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df

    @staticmethod
    def compute_incident_metrics(conn):
        """
        Compute key incident metrics.
        Uses: SELECT, FROM, WHERE, COUNT
        """
        cursor = conn.cursor()

        # Total incidents
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents")
        total = cursor.fetchone()[0]

        # Open incidents
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents WHERE status = 'open'")
        open_count = cursor.fetchone()[0]

        # Critical incidents
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents WHERE severity = 'critical'")
        critical = cursor.fetchone()[0]

        # Phishing incidents
        cursor.execute("SELECT COUNT(*) FROM cyber_incidents WHERE incident_type = 'phishing'")
        phishing_total = cursor.fetchone()[0]

        return total, open_count, critical, phishing_total

    @staticmethod
    def get_daily_phishing_count(conn):
        """
        Get daily counts of phishing incidents.
        Uses: SELECT, FROM, WHERE, GROUP BY, ORDER BY
        """
        query = """
        SELECT date, COUNT(*) as count
        FROM cyber_incidents
        WHERE incident_type = 'phishing'
        GROUP BY date
        ORDER BY date ASC
        """
        df = pd.read_sql_query(query, conn)
        return df
