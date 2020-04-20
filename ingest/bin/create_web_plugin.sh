#! /usr/bin/env bash

set -eou pipefail

echo -n "Enter filename and press [ENTER]: "
read name

cat << EOF > ingest/user_data_sources/$name.py
from apscheduler.triggers.interval import IntervalTrigger
import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def schedule():
    return IntervalTrigger(""" INPUT TIME INTERVAL """)


def init(runtime_id, name):
    return {}


def get_fields():
    return {""" INPUT FIELDS + DATATYPES """}


def fetch_data(db_connection, run_id):

    page = requests.get(""" TARGET URL """)
    soup = BeautifulSoup(page.text, "html.parser")

    items = []

    table = soup.find(""" TARGET TAG """)

    for row in table.find_all("TAG"):
        """RECEIVE DATA"""
        items.append({"x": DATA1, "y": DATA2, "z": DATA3})
    return items


def clean_data(db_connection, run_id, run_data):
    return run_data
EOF