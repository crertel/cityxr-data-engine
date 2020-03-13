from app import app
from flask import url_for, redirect, render_template, flash, g, session
from plugin_manager import PluginManager

import logging

log = logging.getLogger()


@app.route("/")
def root():
    return redirect("/dashboard", 302)


import pprint
import uuid


@app.route("/sources/<source_id>")
def source_details(source_id):

    plugin = PluginManager().get_plugin(uuid.UUID(source_id))
    log.warning(pprint.pformat(PluginManager().get_plugins()))
    return render_template("source.html.j2", ds=plugin)


@app.route("/dashboard")
def dashboard():
    plugins = PluginManager().get_plugins()
    return render_template("dashboard.html.j2", plugins=plugins)
