from database_connection import DatabaseConnection
from data_source import DataSource
from os.path import join
from pathlib import Path


def get_plugin_info(self, run_id, source_id):
    plugins_dir = self.get_user_plugins_dir()
    for file in plugins_dir():
        if file == source_id:
            module_path = join(plugins_dir, file)
        else:
            continue

    module_name = f"{file}"

    data_source = DataSource(
        source_code=Path(module_path).read_text(),
        runtime_id=run_id,
        name=module_name,
        module_path=module_path,
    )
    return data_source


def Reload(run_id, source_id):
    db_connection = DatabaseConnection(run_id)
    db_connection.connect_to_database()
    db_connection.purge_datasource_schema()

    plug = get_plugin_info(run_id, source_id)

    ds = DataSource(plug)
    ds.retstart()
