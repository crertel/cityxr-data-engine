from config import PG_URL
import logging
import json

import psycopg2
from psycopg2 import sql
import psycopg2.extras
from datetime import date, datetime, timezone

psycopg2.extras.register_uuid()


log = logging.getLogger(__name__)


# hack to fix date serialization in json
# from https://stackoverflow.com/a/22238613
def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# Every data source has its own schema.
# Inside that schema are tables for:
# - Data source config information
# - Data source logs
# - Data source run history
# - Data source historical raw data intake
# - Data source current raw data intake
# - Data source historical cleaning
# - Data source current cleaning

DATATYPES = {
    "decimal": "double precision not null",
    "string": "text not null",
    "boolean": "boolean not null",
    "timestamp": "timestamptz not null",
    "date": "date not null",
    "json": "jsonb",
}


def build_sql_for_data_table(
    schema_name, table_name, table_desecription, is_unlogged=False
):
    column_decls = []
    for column_name, data_type in table_desecription.items():
        column_data_decl = DATATYPES[data_type]
        column_decls.append(
            sql.SQL("{column_name} {column_data_decl}").format(
                column_name=sql.Identifier(column_name.lower()),
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
        self._messagingConn = None
        self._cursor = None

    def disconnect_from_database(self):
        if self._conn is not None:
            del self._conn
            self._conn = None
            self._cursor = None
        if self._messagingConn is not None:
            del self._messagingConn
            self._messagingConn = None

    def connect_to_database(self):
        self._conn = psycopg2.connect(PG_URL)
        self._messagingConn = psycopg2.connect(PG_URL)
        self._messagingConn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        self._cursor = self._conn.cursor()

    def send_notification(self, channel, msg):
        if self._messagingConn is not None:
            curs = self._messagingConn.cursor()
            q = sql.SQL("select pg_notify({channel_name}, {payload});").format(
                channel_name=sql.Literal(channel),
                payload=sql.Literal(json.dumps(msg, default=json_serial)),
            )
            curs.execute(q)

    def subscribe_to_notifications(self, channel):
        if self._messagingConn is not None:
            curs = self._messagingConn.cursor()
            curs.execute(
                sql.SQL("listen {channel_name};").format(
                    sql.Identifier(channel_name=channel)
                )
            )

    def poll_notifications(self):
        notifications = []
        if self._messagingConn is not None:
            self._messagingConn.poll()
            while self._messagingConn.notifies:
                notify = self._messagingConn.notifies.pop(0)
                notifications.append((notify.channel, notify.payload))
        return notifications

    def purge_datasource_schema(self):
        purge_ds_schema_sql = sql.SQL(
            """
            drop schema if exists {} cascade;
        """
        ).format(sql.Identifier(self._schema_name))
        self._cursor.execute(purge_ds_schema_sql)
        self._conn.commit()

    def check_if_schema_exists(self):
        schema_name = f"datasource_{self._data_source_runtime_id}"
        schema_exist_sql = """
            select count(*) from information_schema.schemata where schema_name = %s;
        """
        self._cursor.execute(schema_exist_sql, (schema_name,))
        self._conn.commit()
        rows = self._cursor.fetchall()
        return rows[0][0] != 0

    def schema_setup(self, fields):
        fields = {k.lower(): v for k, v in fields.items()}
        # create the schema to hold things
        create_ds_schema_sql = sql.SQL(
            """
            create schema {schema};
        """
        ).format(schema=sql.Identifier(self._schema_name))
        self._cursor.execute(create_ds_schema_sql)
        self._conn.commit()

        # create config schema
        creats_ds_config_sql = sql.SQL(
            """
        create table {schema}.config (
            id text primary key,
            created_at timestamptz not null default now(),
            data_config jsonb not null,
            is_disabled boolean not null default false
        );
        """
        ).format(schema=sql.Identifier(self._schema_name))
        self._cursor.execute(creats_ds_config_sql)
        self._conn.commit()
        update_ds_config_sql = sql.SQL(
            """
        insert into {schema}.config (id, data_config) values (%s,%s);
        """
        ).format(schema=sql.Identifier(self._schema_name))
        self._cursor.execute(
            update_ds_config_sql, (self._data_source_runtime_id, json.dumps(fields),)
        )
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
        self.send_notification(
            self._schema_name,
            {"m": "run_finish", "s": ending_type, "t": datetime.now(timezone.utc)},
        )

    def insert_data(self, table, run_id, data):
        if len(data) > 0:
            data_columns = list(data[0].keys())
            insert_sql = sql.SQL(
                """
            insert into {schema}.{table_name}({data_columns}) values %s;
            """
            ).format(
                schema=sql.Identifier(self._schema_name),
                table_name=sql.Identifier(table),
                data_columns=sql.SQL(",").join(
                    [sql.Identifier(col_name) for col_name in data_columns]
                    + [sql.Identifier("__run_id")]
                ),
            )

            template_params = [f"%({x})s" for x in data_columns]
            template = f"({', '.join(template_params)}, '{run_id}')"

            psycopg2.extras.execute_values(
                self._cursor, insert_sql, data, template=template
            )
            self._conn.commit()

            update_sql = sql.SQL(
                """
            update {schema}.{table_name} set __run_id=%s;
            """
            ).format(
                schema=sql.Identifier(self._schema_name),
                table_name=sql.Identifier(table),
            )
            self._cursor.execute(update_sql, (run_id,))
            self._conn.commit()

    def insert_data_current_raw(self, run_id, data):
        self.insert_data("current_raw", run_id, data)

    def insert_data_current_clean(self, run_id, data):
        self.insert_data("current_clean", run_id, data)

    def archive_data(self, source_table, dest_table, clean_after=False):
        archive_sql = sql.SQL(
            """
        insert into {schema}.{d_table} select * from {schema}.{s_table};
        """
        ).format(
            schema=sql.Identifier(self._schema_name),
            d_table=sql.Identifier(dest_table),
            s_table=sql.Identifier(source_table),
        )
        self._cursor.execute(archive_sql)
        self._conn.commit()

    def archive_raw(self):
        self.archive_data(source_table="current_raw", dest_table="archive_raw")

    def archive_clean(self):
        self.archive_data(source_table="current_clean", dest_table="archive_clean")

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
