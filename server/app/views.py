# from app import app
# from flask import url_for, redirect, render_template, flash, g, session

import logging
from database_connection import DatabaseConnection

log = logging.getLogger()

db_connection = DatabaseConnection()
db_connection.connect_to_database()


def heartbeat():
    return ({"heartbeat": "ok"}, 200)


def get_available_data_sources():
    return (db_connection.get_available_datasources(), 200)
