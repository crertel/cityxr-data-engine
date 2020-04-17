from app import app
from flask import url_for, redirect, render_template, flash, g, session

import logging

log = logging.getLogger()


@app.route("/heartbeat")
def heartbeat():
    return ("Up!", 200)
