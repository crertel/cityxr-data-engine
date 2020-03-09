from plugins.file_data_source import FileDataSource
from time import sleep
import logging

log = logging.getLogger(__name__)


class Plugin(FileDataSource):
    def __init__(self, runtime_id, name):
        # TODO: somehow, we need to pass our three overidden methods back to the base class
        # probably could be some clever kwargs thing, but am too tired to solve it.
        super().__init__(runtime_id, name)

    def migrate_if_needed(db_connection):
        """
        Method called to check if the schema and tables for a data source exist in the DB.
        Does nothing if they do, creates them if they don't.
        """
        log.warning(f"pretending to setup data schema")
        sleep(1)
        pass

    def fetch_data(db_connection, run_id):
        """
        Method called to fetch the data for a run.
        Will insert data along with run into the DB.
        """
        log.warning(f"pretending to fetch data for run {run_id}")
        sleep(1)
        return []

    def clean_data(db_connection, run_id, run_data):
        """
        Method called to clean up the data for a run.
        Will insert the data from a run into the DB.
        """
        log.warning(f"pretending to clean data for run {run_id}")
        sleep(1)
        pass
