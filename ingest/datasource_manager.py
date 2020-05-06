from config import PG_URL
from os.path import join, dirname, abspath, isdir
from os import listdir
from pathlib import Path

import logging
from data_source import DataSource

from util import get_string_sha1

import psycopg2
from psycopg2 import sql
import psycopg2.extras

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

psycopg2.extras.register_uuid()


class DatasourceManager(object):
    _plugins = {}
    _instance = None
    _conn = None
    _cursor = None

    def __new__(clazz):
        if clazz._instance is None:
            clazz._instance = super(DatasourceManager, clazz).__new__(clazz)
        return clazz._instance

    def get_plugins(self):
        return self._plugins

    def get_plugin(self, pid):
        return self._plugins.get(pid)

    def get_user_plugins_dir(self):
        script_path = abspath(__file__)
        script_dir = dirname(script_path)
        return join(script_dir, "user_datasources")

    def update_sources(self):
        for (sid, source) in self._plugins.items():
            source.update()

    def get_run_logs_for_plugin(self, source_id, limit=None):
        _conn = psycopg2.connect(PG_URL)
        _cursor = _conn.cursor()
        if limit is None:
            fetch_run_log_sql = sql.SQL(
                """
                select id, started_at, ended_at, state from {table_name}.runs
                order by started_at desc;
            """
            ).format(table_name=sql.Identifier("datasource_" + source_id))
            _cursor.execute(fetch_run_log_sql)
        else:
            fetch_run_log_sql = sql.SQL(
                """
                select id, started_at, ended_at, state from {table_name}.runs
                order by started_at desc
                limit %s;
            """
            ).format(table_name=sql.Identifier("datasource_" + source_id))
            _cursor.execute(fetch_run_log_sql, (limit,))

        ret = _cursor.fetchall()
        _conn.close()
        return ret

    def get_run_logs_for_plugin_run(self, source_id, run_id, limit=None):
        _conn = psycopg2.connect(PG_URL)
        _cursor = _conn.cursor()
        if limit is None:
            fetch_run_log_sql = sql.SQL(
                """
                select time, severity, msg from {table_name}.log where run = %s
                order by time desc;
            """
            ).format(table_name=sql.Identifier("datasource_" + source_id))
            _cursor.execute(fetch_run_log_sql, (run_id,))
        else:
            fetch_run_log_sql = sql.SQL(
                """
                select time, severity, msg from {table_name}.log where run = %s
                order by time desc
                limit %s;
            """
            ).format(table_name=sql.Identifier("datasource_" + source_id))
            log.error(f">>> {_cursor.mogrify(fetch_run_log_sql, (run_id, limit,))}")
            _cursor.execute(fetch_run_log_sql, (run_id, limit,))

        ret = _cursor.fetchall()
        _conn.close()
        return ret

    def load_sources(self):
        log.warning(f"Loading sources...")
        plugins_dir = self.get_user_plugins_dir()
        for file in listdir(plugins_dir):
            module_path = join(plugins_dir, file)
            if isdir(module_path) or not module_path.endswith(".py"):
                continue

            module_name = f"{file}"
            log.warning(f"\tloading plugin {module_name} ({module_path})...")
            dsid = get_string_sha1(module_name)

            data_source = DataSource(
                source_code=Path(module_path).read_text(),
                runtime_id=dsid,
                name=module_name,
                module_path=module_path,
            )
            self._plugins[dsid] = data_source
