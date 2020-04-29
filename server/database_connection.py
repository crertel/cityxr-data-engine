from config import PG_URL
import logging

import psycopg2
from psycopg2 import sql
import psycopg2.extras

psycopg2.extras.register_uuid()

log = logging.getLogger(__name__)

DATATYPES = {
    "decimal": "double precision not null",
    "string": "text not null",
    "boolean": "boolean not null",
    "timestamp": "timestamptz not null",
    "date": "date not null",
    "json": "jsonb",
}


class DatabaseConnection:
    def __init__(self):
        self._conn = None
        self._cursor = None

    def connect_to_database(self):
        self._conn = psycopg2.connect(PG_URL)
        self._cursor = self._conn.cursor()

    def get_available_datasources(self):
        datasources_sql = """
        select
            datasource_id, created_at, config, is_disabled
        from
            cxr_db.get_available_datasources();
        """
        self._cursor.execute(datasources_sql)
        self._conn.commit()
        rows = self._cursor.fetchall()
        ret = {}
        for (datasource_id, created_at, config, is_disabled) in rows:
            ret[datasource_id.__str__()] = {
                "created_at": created_at,
                "is_disabled": is_disabled,
                "config": config,
            }
        return ret

    def check_if_schema_exists(self, schema_runtime_id):
        schema_name = f"datasource_{schema_runtime_id}"
        schema_exist_sql = """
            select count(*) from information_schema.schemata where schema_name = %s;
        """
        self._cursor.execute(schema_exist_sql, (schema_name,))
        self._conn.commit()
        rows = self._cursor.fetchall()
        return rows[0][0] != 0
