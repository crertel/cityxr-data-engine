#! /usr/bin/env bash

set -eou pipefail

echo -n "Enter filename and press [ENTER]: "
read name

cat << EOF > ingest/user_data_sources/$name.py
from apscheduler.triggers.interval import IntervalTrigger


def schedule():
    """
    Gets the scheduled run for the data source.
    Returns the scheduled time for the data source.
    """
    return IntervalTrigger(seconds=6)


def init(runtime_id, name):
    """
    Intializes the data source.
    Returns the initial state of the data source.
    """
    return {}


def get_fields():
    return {"a": "decimal"}


def fetch_data(db_connection, run_id):
    """
    Fetches the data for a run.
    Will insert data along with run into the DB.
    """
    return []


def clean_data(db_connection, run_id, run_data):
    """
    Cleans up the data for a run.
    Will insert the data from a run into the DB.
    """
    return run_data
EOF