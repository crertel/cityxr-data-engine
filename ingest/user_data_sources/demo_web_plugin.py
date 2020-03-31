from apscheduler.triggers.interval import IntervalTrigger

import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def schedule():
    return IntervalTrigger(seconds=10)


def init(runtime_id, name):
    return {}


def get_fields():
    return {
        "station": "string",
        "route": "string",
        "address": "string",
        "travel_time_from_transit_center": "string",
    }


def fetch_data(db_connection, run_id):

    page = requests.get("https://www.ridemetro.org/Pages/RedLine.aspx")
    soup = BeautifulSoup(page.text, "html.parser")

    items = []

    table = soup.find(class_="table table-bordered table-striped")
    station_table = table.find("tbody")

    log.warning(f"fetching metro data {run_id}")

    for row in station_table.find_all("tr"):
        name = row.contents[1]
        route = row.contents[3]
        addr = row.contents[5]
        ttime = row.contents[7]
        items.append(
            {
                "station": name.contents[0].strip(),
                "route": route.contents[0].strip(),
                "address": addr.contents[0].strip(),
                "travel_time_from_transit_center": ttime.contents[0].strip(),
            }
        )
    return items


def clean_data(db_connection, run_id, run_data):
    return run_data
