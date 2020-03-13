from os.path import join, dirname, abspath
from os import listdir

import logging
from data_source import DataSource

from uuid import uuid4

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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
        return join(script_dir, "user_data_sources")

    def load_plugins(self):
        log.warning(f"Loading plugins...")
        plugins_dir = self.get_user_plugins_dir()
        for file in listdir(plugins_dir):
            if file == "__pycache__":
                continue
            module_path = join(plugins_dir, file)
            module_name = f"{file}"
            log.warning(f"\tloading plugin {module_name} ({module_path})...")
            dsid = uuid4()
            data_source = DataSource(
                runtime_id=dsid, name=module_name, module_path=module_path
            )
            self._plugins[dsid] = data_source
