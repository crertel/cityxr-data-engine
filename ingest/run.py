from plugin_manager import PluginManager
from os import environ

from app import app
from config import LISTEN_PORT, DEBUG, PG_URL

from threading import Thread

import psycopg2


db_conn = psycopg2.connect(PG_URL)
db_cursor = db_conn.cursor()
db_cursor.execute(
    """
create extension if not exists "uuid-ossp";
"""
)
db_conn.commit()
db_cursor.execute(
    """
create schema if not exists "cxr_db";
"""
)
db_conn.commit()

db_cursor.execute("drop function if exists cxr_db.get_available_datasources;")
db_conn.commit()

db_cursor.execute(
    """
create or replace function cxr_db.get_available_datasources()
returns table (
    datasource_id text,
    created_at timestamptz,
    config jsonb,
    is_disabled boolean
)
as $BODY$
declare
    sname text;
begin
    for sname in
      select schema_name from information_schema.schemata where schema_name like 'datasource_%'
    loop
        return query execute format( 'select * from %I.config', sname );

    end loop;
    return;
end
$BODY$ language plpgsql stable;

"""
)
db_conn.commit()

db_cursor.close()
db_conn.close()


def pump_sources():
    while 1:
        pm.update_sources()


if environ.get("WERKZEUG_RUN_MAIN") == "true":
    pm = PluginManager()
    pm.load_sources()
    source_thread = Thread(daemon=True, target=pump_sources)
    source_thread.start()

if DEBUG:
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(host="0.0.0.0", debug=DEBUG, port=LISTEN_PORT)
