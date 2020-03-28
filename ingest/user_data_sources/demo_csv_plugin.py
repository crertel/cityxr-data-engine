from datetime import date
import time
import csv
from apscheduler.triggers.interval import IntervalTrigger
from os.path import join, dirname, abspath
import logging

log = logging.getLogger(__name__)

script_path = abspath(__file__)
script_dir = dirname(script_path)


def schedule():
    return IntervalTrigger(seconds=5)


def init(runtime_id, name):
    return {}


def get_fields():
    return {"date": "date", "high": "decimal", "low": "decimal"}


def fetch_data(db_connection, run_id):
    ret = []
    csv_path = join(script_dir, "../datasets/sampleTemp.csv")
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            pdate = time.strptime(row[0], "%d/%m/%Y")
            row_date = date(year=pdate.tm_year, month=pdate.tm_mon, day=pdate.tm_mday)
            row_high = float(row[1])
            row_low = float(row[2])
            ret.append({"date": row_date, "high": row_high, "low": row_low})
    return ret


def clean_data(db_connection, run_id, run_data):
    return run_data
