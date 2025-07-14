from decimal import Decimal
from db_access.config_dao import ConfigDAO
import db_access.db_init as dbinit
import duckdb

conn = duckdb.connect()

def test_base_query():
    cfg_dao = ConfigDAO(conn)
    result = cfg_dao.dummy_query()
    assert result == [(42,)]
    
def test_table_query():
    dbinit.create_db(conn)
    result = conn.sql("SELECT * FROM test").fetchall()
    assert result == [(1, 'jeans', Decimal('20.00'), 1), (2, 'hammer', Decimal('42.20'), 2)]