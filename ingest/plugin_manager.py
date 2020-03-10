from os.path import join, dirname, abspath
from os import listdir
import importlib.util

import logging
from data_source import DataSource

from uuid import uuid4

log = logging.getLogger(__name__)


class PluginManager(object):
    _plugins = {}
    _instance = None

    def __new__(clazz):
        if clazz._instance is None:
            clazz._instance = super(PluginManager, clazz).__new__(clazz)
        return clazz._instance

    def get_plugins(self):
        return self._plugins

    def get_user_plugins_dir(self):
        script_path = abspath(__file__)
        script_dir = dirname(script_path)
        return join(script_dir, "user_plugins")

    def load_plugins(self):
        log.info(f"Loading plugins...")
        plugins_dir = self.get_user_plugins_dir()
        for file in listdir(plugins_dir):
            if file == "__pycache__":
                continue
            plugin_path = join(plugins_dir, file)
            module_name = f"{file}"
            log.info(f"\tloading plugin {module_name} ({plugin_path})...")
            spec = importlib.util.spec_from_file_location(
                f"plugin_{module_name}", plugin_path
            )
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            plugin_uuid = uuid4()
            data_source = DataSource(
                plugin_uuid,
                module_name,
                schedule_cb=plugin_module.schedule,
                init_cb=plugin_module.init,
                migrate_cb=plugin_module.migrate_if_needed,
                fetch_cb=plugin_module.fetch_data,
                clean_cb=plugin_module.clean_data,
            )
            self._plugins[plugin_uuid] = data_source
