import pandas as pd
from app.data.db import connect_database

class Dataset:
    """ Contains all dataset-related data.
    This class handles retrieving datasets, and performing CRUD operations on the datasets_metadata database."""
    def __init__(self, dataset_name, category, source, last_updated, record_count, file_size_mb, created_at=None,id=None):
        self.dataset_name = dataset_name
        self.category = category
        self.source = source
        self.last_updated = last_updated
        self.record_count = record_count
        self.file_size_mb = file_size_mb
        self.created_at = created_at
        self.id = id

    def __str__(self):
        return f"Dataset(id={self.id}, name={self.dataset_name}, category={self.category}, source={self.source}, last_updated={self.last_updated}, record_count={self.record_count}, file_size_mb={self.file_size_mb})"


    # CRUD Methods

    @staticmethod
    def get_all_datasets(conn):
        """Get all datasets as DataFrame.
        """
        df = pd.read_sql_query(
            "SELECT * FROM datasets_metadata ORDER BY id DESC",
            conn
        )
        #conn.close()
        return df


    def insert_dataset(self):
        """Insert new dataset into database.
        Returns:
            ID of the newly inserted dataset"""
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO datasets_metadata 
            (dataset_name, category, source, last_updated, record_count, file_size_mb)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.dataset_name, self.category, self.source, self.last_updated, self.record_count, self.file_size_mb))
        conn.commit()
        dataset_id = cursor.lastrowid # Get the ID of the newly inserted dataset
        conn.close()
        return dataset_id

    @staticmethod
    def update_last_updated_date(conn, dataset_id, new_last_updated):
        """Update the last_updated date of a dataset.
        Args:
            conn (sqlite3.Connection): Open database connection.
            dataset_id = ID of the dataset to be updated
            new_last_updated = New last updated date in 'YYYY-MM-DD' format
        Returns:
            Number of rows that were updated"""
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE datasets_metadata SET last_updated = ? WHERE id = ?",
            (new_last_updated, dataset_id)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    @staticmethod
    def delete_dataset(conn, id: int):
        """Delete a dataset.
        Args:
            conn (sqlite3.Connection): Open database connection.
            dataset_id = ID of the row to be deleted
        Returns:
            Number of rows that were deleted"""
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM datasets_metadata WHERE id = ?",
            (id,)
        )
        conn.commit()
        conn.close()
        return cursor.rowcount

    # Analytics Methods

    @staticmethod
    def get_resource_consumption_by_category(conn):
        """
        Analyze total resource consumption (size and record count) by category.
        Identifies which categories consume the most resources.
        Uses: SELECT, FROM, GROUP BY, SUM, ORDER BY
        """
        query = """
        SELECT 
            category,
            COUNT(*) as dataset_count,
            SUM(record_count) as total_records,
            ROUND(SUM(file_size_mb), 2) as total_size_mb
        FROM datasets_metadata
        GROUP BY category
        ORDER BY total_size_mb DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    
    @staticmethod
    def get_datasets_by_source_count(conn):
        """
        Count datasets by source (internal, external, public, partner).
        Helps understand data source dependency.
        Uses: SELECT, FROM, GROUP BY, ORDER BY
        """
        query = """
        SELECT source, COUNT(*) as count
        FROM datasets_metadata
        GROUP BY source
        ORDER BY count DESC
        """
        df = pd.read_sql_query(query, conn)
        return df

