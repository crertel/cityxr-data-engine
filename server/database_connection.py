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

    def get_most_recent_run_for_datasource(self, datasource_id):
        if not self.check_if_schema_exists(datasource_id):
            return None

        schema_name = f"datasource_{datasource_id}"
        run_fetch_sql = sql.SQL(
            """
            select * from {schema}.archive_clean as data
            where data.__run_id in (
                select id as run_id from  {schema}.runs
                where state = 'succeeded'
                order by started_at desc
                limit 1
            );
        """
        ).format(schema=sql.Identifier(schema_name))

        self._cursor.execute(run_fetch_sql, (schema_name,))
        self._conn.commit()
        return {
            "data": self._cursor.fetchall(),
            "columns": [desc[0] for desc in self._cursor.description],
        }

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
                "createdAt": created_at,
                "isDisabled": is_disabled,
                "config": config,
            }
        return ret

    def check_if_schema_exists(self, datasource_runtime_id):
        schema_name = f"datasource_{datasource_runtime_id}"
        schema_exist_sql = """
            select count(*) from information_schema.schemata where schema_name = %s;
        """
        self._cursor.execute(schema_exist_sql, (schema_name,))
        self._conn.commit()
        rows = self._cursor.fetchall()
        return rows[0][0] != 0
