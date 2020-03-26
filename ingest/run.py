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
