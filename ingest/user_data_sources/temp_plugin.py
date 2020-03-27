from time import sleep
import logging
import csv

from apscheduler.triggers.interval import IntervalTrigger


log = logging.getLogger(__name__)


def schedule():
    """
    Gets the scheduled run for the data source.
    Returns the scheduled time for the data source.
    """
    # lolwut
    log.warning("say something pls")
    return IntervalTrigger(seconds=5)


def init(runtime_id, name):
    """
    Intializes the data source.
    Returns the initial state of the data source.
    """

    return {}


def get_fields():
    return {"date": "date", "high": "decimal", "low": "decimal"}


def fetch_data(db_connection, run_id):
    """
    Fetches the data for a run.
    Will insert data along with run into the DB.
    """
    fig = []
    log.warning(f"fetching temp data for run {run_id}")
    sleep(1)
    x = 0
    with open("ingest/datasets/sampleTemp.csv", newline="") as csvfile:
        tempTest = csv.reader(csvfile, delimiter=",")
        for row in tempTest:
            return [{"date": row[0]}, {"high": row[1]}, {"low": row[2]}]
            row_date = row[0]
            row_high = row[1]
            row_low = row[2]
            fig.append({"date": row_date, "high": row_high, "low": row_low})

            log.message(x)
            x += 1
    return fig


def clean_data(db_connection, run_id, run_data):
    """
    Cleans up the data for a run.
    Will insert the data from a run into the DB.
    """
    log.warning(f"cleaning temperature data for run {run_id}")
    sleep(1)
    return run_data
