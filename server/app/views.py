# from app import app
# from flask import url_for, redirect, render_template, flash, g, session

import logging
from datetime import datetime
from database_connection import DatabaseConnection

log = logging.getLogger()

db_connection = DatabaseConnection()
db_connection.connect_to_database()

boot_time = datetime.utcnow()


def heartbeat():
    now = datetime.utcnow()
    return ({"bootTime": boot_time, "uptime": (now - boot_time).total_seconds()}, 200)


def get_available_data_sources():
    return (db_connection.get_available_datasources(), 200)


def get_latest_data_for_source(datasource_id):
    res = db_connection.get_most_recent_run_for_datasource(datasource_id)
    if res is None:
        return ({"error": f"can't find datasource {datasource_id}"}, 404)
    elif res is False:
        return ({"error": f"no finished runs for datasource {datasource_id}"}, 404)
    else:
        return (res, 200)


def get_historical_data_for_source(datasource_id, start_time, end_time):
    res = db_connection.get_data_for_datasource_for_time_range(
        datasource_id=datasource_id, start_time=start_time, end_time=end_time
    )
    if res is None:
        return ({"error": f"can't find datasource {datasource_id}"}, 404)
    elif res is False:
        return (
            {
                "error": f"no finished runs for datasource {datasource_id} on timeframe {start_time} to {end_time} "
            },
            404,
        )
    else:
        return (res, 200)

