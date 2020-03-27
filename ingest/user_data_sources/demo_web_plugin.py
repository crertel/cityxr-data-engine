import time
from apscheduler.triggers.interval import IntervalTrigger
from os.path import join, dirname, abspath
import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

script_path = abspath(__file__)
script_dir = dirname(script_path)


def schedule():
    return IntervalTrigger(seconds=10)


def init(runtime_id, name):
    return {}


def get_fields():
    return {
        "station": "string",
        "Route": "string",
        "Address": "string",
        "Travel Time From Transit Center": "string",
    }


def fetch_data(db_connection, run_id):

    page = requests.get("https://www.ridemetro.org/Pages/RedLine.aspx")
    soup = BeautifulSoup(page.text, "html.parser")

    items = []

    table = soup.find(class_="table table-bordered table-striped")
    station_table = table.find("tbody")

    for row in station_table.find_all("tr"):
        name = row.contents[1]
        route = row.contents[3]
        addr = row.contents[5]
        ttime = row.contents[7]
        items.append(
            {
                "Station": name.contents[0].strip(),
                "Direction": route.contents[0].strip(),
                "Location": addr.contents[0].strip(),
                "Travel Time": ttime.contents[0].strip(),
            }
        )
    return items
    log.warning(f"fetching metro data {run_id}")


def clean_data(db_connection, run_id, run_data):
    return run_data
