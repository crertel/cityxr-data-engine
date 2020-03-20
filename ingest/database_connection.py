import psycopg2
from psycopg2 import sql
from config import PG_URL
from pprint import pformat
import logging

log = logging.getLogger(__name__)


# Every data source has its own schema.
# Inside that schema are tables for:
# - Data source logs
# - Data source run history
# - Data source historical raw data intake
# - Data source current raw data intake
# - Data source historical cleaning
# - Data source current cleaning


class DatabaseConnection:
    def __init__(self, data_source_runtime_id):
        self._data_source_runtime_id = data_source_runtime_id
        self._schema_name = f"datasource_{data_source_runtime_id}"
        self._conn = None
        self._cursor = None

    def conect_to_database(self):
        self._conn = psycopg2.connect(PG_URL)
        self._cursor = self._conn.cursor()

    def check_if_schema_exists(self):
        sql = """
            select schema_name from information_schema.schemata;
        """
        self._cursor.execute(sql)
        self._conn.commit()
        rows = self._cursor.fetchall()
        log.error(pformat(rows))
        if not (f"datasource_{self._data_source_runtime_id}",) in rows:
            return False
        return True

    def schema_setup(self, fields):
        # create the schema to hold things
        create_ds_schema_sql = sql.SQL(
            """
            create schema {};
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(create_ds_schema_sql)
        self._conn.commit()

        # create log schema
        create_ds_log_sql = sql.SQL(
            """
        create extension if not exists "uuid-ossp";
        create table {}.log (
            id uuid primary key default uuid_generate_v4(),
            time timestamp with timezone not null default now(),
            msg text not null,
            run uuid not null default uuid_nil()
        );
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(create_ds_log_sql)
        self._conn.commit()

        # create runs schema
        create_ds_runs_sql = sql.SQL(
            """
        create table {}.runs (
            id uuid primary key,
            started_at timestamp with timezone not null default now(),
            ended_at timestamp with timezone not null default infinity,
            state text not null
        );
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(create_ds_runs_sql)
        self._conn.commit()

    def log_message(self, time, message, run_id):
        log_sql = sql.SQL(
            """
        insert into {}.log(time, msg, run) values (%s,%s,%s);
        """
        ).format(sql.Identifier(self._schema_name))

        self._cursor.execute(log_sql, (time, message, run_id))
        self._conn.commit()

    def log_messages(self, messages):
        log_sql = sql.SQL(
            """
        insert into {}.log(time, msg, run) values %s;
        """
        ).format(sql.Identifier(self._schema_name))

        # from docs, this is less gross:
        # https://www.psycopg.org/docs/extras.html#psycopg2.extras.execute_values
        psycopg2.extras.execute_values(self._cursor, log_sql, messages)
        self._conn.commit()
