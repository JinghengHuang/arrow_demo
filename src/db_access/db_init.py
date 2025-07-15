# Script to initialize the DuckDB storage based on table structure
# Finish after table structure is confirmed
import duckdb

class DBManagement():
        
    def create_db(conn:duckdb.DuckDBPyConnection):
        # test table
        conn.execute("""
            CREATE TABLE test (id INTEGER PRIMARY KEY, item VARCHAR, value DECIMAL(10, 2), count INTEGER)
            """)
        # Test data
        conn.execute("INSERT INTO test VALUES (1, 'jeans', 20.0, 1), (2, 'hammer', 42.2, 2)")
        # rest of the tables. To be added when DB design is confirmed.