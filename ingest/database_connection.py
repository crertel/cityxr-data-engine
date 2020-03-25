from config import PG_URL
from pprint import pformat
import logging

import psycopg2
from psycopg2 import sql
import psycopg2.extras

psycopg2.extras.register_uuid()


log = logging.getLogger(__name__)


# Every data source has its own schema.
# Inside that schema are tables for:
# - Data source logs
# - Data source run history
# - Data source historical raw data intake
# - Data source current raw data intake
# - Data source historical cleaning
# - Data source current cleaning
def build_sql_for_data_table(
    schema_name, table_name, table_desecription, is_unlogged=False
):
    DATATYPES = {
        "decimal": "double precision not null",
        "string": "text not null",
        "boolean": "boolean not null",
        "timestamp": "timestamptz not null",
    }

    column_decls = []
    for column_name, data_type in table_desecription.items():
        column_data_decl = DATATYPES[data_type]
        column_decls.append(
            sql.SQL("{column_name} {column_data_decl}").format(
                column_name=sql.Identifier(column_name),
                column_data_decl=sql.SQL(column_data_decl),
            )
        )

    logged_table_decl = sql.SQL("create table")
    unlogged_table_decl = sql.SQL("create unlogged table")

    return sql.SQL(
        """
        {table_decl} {schema}.{table_name} (
            __id uuid primary key default uuid_generate_v4(),
            __run_id uuid not null,
            {column_decls}
        );
        create index on {schema}.{table_name}(__id);
        create index on {schema}.{table_name}(__run_id);
        """
    ).format(
        table_decl=unlogged_table_decl if is_unlogged else logged_table_decl,
        schema=sql.Identifier(schema_name),
        table_name=sql.Identifier(table_name),
        column_decls=sql.SQL(",").join(column_decls),
    )


class DatabaseConnection:
    def __init__(self, data_source_runtime_id):
        self._data_source_runtime_id = data_source_runtime_id
        self._schema_name = f"datasource_{data_source_runtime_id}"
        self._conn = None
        self._cursor = None

    def conect_to_database(self):
        self._conn = psycopg2.connect(PG_URL)
        self._cursor = self._conn.cursor()

    def purge_datasource_schema(self):
        purge_ds_schema_sql = sql.SQL(
            """
            drop schema if exists {} cascade;
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(purge_ds_schema_sql)
        self._conn.commit()

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
        create table {}.log (
            id uuid primary key default uuid_generate_v4(),
            time timestamptz not null default now(),
            severity text not null,
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
            started_at timestamptz not null default now(),
            ended_at timestamptz not null default 'infinity'::timestamptz,
            state text not null
        );
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(create_ds_runs_sql)
        self._conn.commit()

        self._cursor.execute(
            build_sql_for_data_table(self._schema_name, "archive_raw", fields)
        )
        self._conn.commit()
        self._cursor.execute(
            build_sql_for_data_table(self._schema_name, "archive_clean", fields)
        )
        self._conn.commit()
        self._cursor.execute(
            build_sql_for_data_table(
                self._schema_name, "current_raw", fields, is_unlogged=True
            )
        )
        self._conn.commit()
        self._cursor.execute(
            build_sql_for_data_table(
                self._schema_name, "current_clean", fields, is_unlogged=True
            )
        )
        self._conn.commit()

    def empty_table(self, table_name):
        truncate_sql = sql.SQL(
            """
            truncate {schema}.{table_name};
            """
        ).format(
            schema=sql.Identifier(self._schema_name),
            table_name=sql.Identifier(table_name),
        )
        self._cursor.execute(truncate_sql)
        self._conn.commit()

    def empty_current_raw_table(self):
        self.empty_table("current_raw")

    def empty_current_clean_table(self):
        self.empty_table("current_clean")

    def begin_run(self, run_id):
        log_sql = sql.SQL(
            """
        insert into {}.runs(id, started_at, state) values (%s, now(), 'running');
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(log_sql, (run_id,))
        self._conn.commit()

    def update_run(self, run_id, curr_state):
        update_run_sql = sql.SQL(
            """
        update {}.runs
        set
            state = %s
        where
            id = %s;
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(update_run_sql, (curr_state, run_id))
        self._conn.commit()

    def end_run(self, run_id, ending_type):
        end_run_sql = sql.SQL(
            """
        update {}.runs
        set
            ended_at = now(),
            state = %s
        where
            id = %s;
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(end_run_sql, (ending_type, run_id))
        self._conn.commit()

    def insert_data_current_raw(self, run_id, data_columns, data):
        insert_sql = sql.SQL(
            """
        insert into {schema}.current_raw({data_columns}) values %s;
        """
        ).format(
            schema=sql.Identifier(self._schema_name),
            data_columns=sql.SQL(",").join(
                [sql.Identifier(col_name) for col_name in data_columns]
            ),
        )
        psycopg2.extras.execute_values(self._cursor, insert_sql, data)
        self._conn.commit()

        update_sql = sql.SQL(
            """
        update {schema}.current_raw set __run_id=%s;
        """
        ).format(schema=sql.Identifier(self._schema_name),)
        self._cursor.execute(update_sql, (run_id,))
        self._conn.commit()

    def insert_data_current_clean(self, run_id, data_columns, data):
        insert_sql = sql.SQL(
            """
        insert into {schema}.current_clean({data_columns}) values %s;
        """
        ).format(
            schema=sql.Identifier(self._schema_name),
            data_columns=sql.SQL(",").join(
                [sql.Identifier(col_name) for col_name in data_columns]
            ),
        )
        psycopg2.extras.execute_values(self._cursor, insert_sql, data)
        self._conn.commit()

        update_sql = sql.SQL(
            """
        update {schema}.current_clean set __run_id=%s;
        """
        ).format(schema=sql.Identifier(self._schema_name),)
        self._cursor.execute(update_sql, (run_id,))
        self._conn.commit()

    def archive_raw(self):
        archive_sql = sql.SQL(
            """
        select * into  {}.archive_raw from {}.current_raw;
        """
        ).format((sql.Identifier(self._schema_name), sql.Identifier(self._schema_name)))
        self._cursor.execute(archive_sql)
        self._conn.commit()
        self.empty_current_raw_table()

    def archive_clean(self):
        archive_sql = sql.SQL(
            """
        select * into  {}.archive_clean from {}.current_clean;
        """
        ).format((sql.Identifier(self._schema_name), sql.Identifier(self._schema_name)))
        self._cursor.execute(archive_sql)
        self._conn.commit()
        self.empty_current_clean_table()

    def log(self, time, severity, message, run_id):
        log_sql = sql.SQL(
            """
        insert into {}.log(time, severity, msg, run) values (%s,%s,%s, %s);
        """
        ).format(sql.Identifier(self._schema_name))

        self._cursor.execute(log_sql, (time, severity, message, run_id))
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
