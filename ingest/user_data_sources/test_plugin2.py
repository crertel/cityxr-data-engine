from time import sleep
import logging

from apscheduler.triggers.interval import IntervalTrigger


log = logging.getLogger(__name__)


def schedule():
    """
    Gets the scheduled run for the data source.
    Returns the scheduled time for the data source.
    """
    return IntervalTrigger(seconds=20)


def init(runtime_id, name):
    """
    Intializes the data source.
    Returns the initial state of the data source.
    """
    return {}


def migrate_if_needed(db_connection):
    """
    Checks if the schema and tables for a data source exist in the DB.
    Does nothing if they do, creates them if they don't.
    """
    log.warning(f"CHONKY pretending to setup data schema")
    sleep(1)


def fetch_data(db_connection, run_id):
    """
    Fetches the data for a run.
    Will insert data along with run into the DB.
    """
    log.warning(f"CHONKY pretending to fetch data for run {run_id}")
    sleep(1)
    return []


def clean_data(db_connection, run_id, run_data):
    """
    Cleans up the data for a run.
    Will insert the data from a run into the DB.
    """
    log.warning(f"CHONKY pretending to clean data for run {run_id}")
    sleep(1)
