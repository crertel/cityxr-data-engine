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
