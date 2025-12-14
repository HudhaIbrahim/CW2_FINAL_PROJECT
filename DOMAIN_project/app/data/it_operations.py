import pandas as pd
from app.data.db import connect_database

class Tickets:
    """ IT Tickets Data Model and Operations """
    def __init__(self, ticket_id, status, category, subject, description, created_date, resolved_date, assigned_to, id=None, created_at=None):
        self.id = id
        self.ticket_id = ticket_id
        self.status = status
        self.category = category
        self.subject = subject
        self.description = description
        self.created_date = created_date
        self.resolved_date = resolved_date
        self.assigned_to = assigned_to
        self.created_at = created_at

    def __str__(self):
        return f"ticket_id={self.ticket_id}, status={self.status}, category={self.category}, subject={self.subject}, assigned_to={self.assigned_to}, created_date={self.created_date}, resolved_date={self.resolved_date}, description={self.description}"
    
    @staticmethod
    def get_all_tickets(conn):
        """Get all tickets as DataFrame."""
        df = pd.read_sql_query(
            "SELECT * FROM it_tickets ORDER BY ticket_id DESC",
            conn
        )
        return df

    # CRUD methods

    def insert_ticket(self):
        """Insert new ticket to the database.
        Returns:
            ID of the ticket that was inserted to the database"""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO it_tickets 
            (ticket_id, status, category, subject, descripton, created_date, resolved_date, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (self.ticket_id, self.status, self.category, self.subject, self.description, self.created_date, self.resolved_date, self.assigned_to))
        conn.commit()
        ticket_id = cursor.lastrowid # Get the ID of the inserted ticket
        conn.close()
        return ticket_id

    @staticmethod
    def update_ticket_status(conn, ticket_id: int, new_status: str):
        """Update an existing ticket status.
        Args:
            ticket_id (int): ID of ticket to be updated.
            new_status (str): New status of the ticket.
            conn (sqlite3.Connection): Database connection.
        Returns:
            Number of rows updated."""
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
            (new_status, ticket_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    @staticmethod
    def delete_ticket(conn, ticket_id):
        """Delete incident.
        Args:
            conn (sqlite3.Connection): Database connection.
            ticket_id (int): ID of ticket to be deleted.
        Returns:
            Number of rows deleted."""
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM it_tickets WHERE ticket_id = ?",
            (ticket_id,)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    # Analytics methods

    @staticmethod
    def get_tickets_resolved_by_staff(conn):
        """Simple version - counts tickets per staff member"""
        query = """
        SELECT 
            assigned_to,
            COUNT(*) as total_tickets,
            SUM(CASE WHEN status = 'resolved' OR status = 'closed' THEN 1 ELSE 0 END) as resolved_tickets
        FROM it_tickets
        WHERE assigned_to IS NOT NULL
        GROUP BY assigned_to
        ORDER BY resolved_tickets DESC
        """
        return pd.read_sql_query(query, conn)


    @staticmethod
    def get_ticket_kpis(conn):
        """Get key performance indicators"""
        cursor = conn.cursor()
        
        # Total tickets
        total = cursor.execute("SELECT COUNT(*) FROM it_tickets").fetchone()[0]
        
        # Open tickets
        open_count = cursor.execute("SELECT COUNT(*) FROM it_tickets WHERE status = 'open'").fetchone()[0]
        
        # Unresolved tickets
        unresolved = cursor.execute(
            "SELECT COUNT(*) FROM it_tickets WHERE resolved_date IS NULL"
        ).fetchone()[0]
        return total, open_count, unresolved