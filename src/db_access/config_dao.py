from db_access.base_dao import BaseDAO

class ConfigDAO(BaseDAO):
    def dummy_query(self):
        return self._conn.execute("""
                                SELECT 42
                                """).fetchall()