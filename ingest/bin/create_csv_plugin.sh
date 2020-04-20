#! /usr/bin/env bash

set -eou pipefail

echo -n "Enter filename and press [ENTER]: "
read name

cat << EOF > ingest/user_data_sources/$name.py
import csv
from apscheduler.triggers.interval import IntervalTrigger
from os.path import join, dirname, abspath
import logging

log = logging.getLogger(__name__)

script_path = abspath(__file__)
script_dir = dirname(script_path)


def schedule():
    return IntervalTrigger(""" INPUT TIME INTERVAL """)


def init(runtime_id, name):
    return {}


def get_fields():
    return {""" INPUT FIELDS + DATATYPES """}


def fetch_data(db_connection, run_id):
    items = []
    csv_path = join(script_dir, "../datasets/YOURFILENAME ")
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            """RECEIVE DATA"""
            items.append({"x": DATA1, "y": DATA2, "z": DATA3})
    return items


def clean_data(db_connection, run_id, run_data):
    return run_data
EOF