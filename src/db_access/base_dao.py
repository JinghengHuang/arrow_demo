import duckdb

class BaseDAO():
    def __init__(self, db_conn: duckdb.DuckDBPyConnection):
        self._conn = db_conn
    