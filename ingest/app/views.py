from app import app
from flask import url_for, redirect, render_template, flash, g, session
from plugin_manager import PluginManager
from reload_and_purge import Reload

import logging

log = logging.getLogger()


@app.route("/")
def root():
    return redirect("/dashboard", 302)


@app.route("/sources/<source_id>")
def source_details(source_id):
    ds = PluginManager().get_plugin(source_id)
    ds_run_logs = PluginManager().get_run_logs_for_plugin(source_id=source_id, limit=10)
    return render_template("source.html.j2", ds=ds, ds_run_log=ds_run_logs)


@app.route("/sources/<source_id>/runs/<run_id>/logs")
def run_log_details(source_id, run_id):
    run_log = PluginManager().get_run_logs_for_plugin_run(
        source_id=source_id, run_id=run_id, limit=10
    )
    return render_template("logs.html.j2", log_messages=run_log)


@app.route("/dashboard")
def dashboard():
    plugins = PluginManager().get_plugins()
    return render_template("dashboard.html.j2", plugins=plugins)


@app.route("/sources/<run_id>/purge_and_reload")
def restart_button(source_id, run_id):
    Reload(run_id=run_id, source_id=source_id)
    return render_template("reset.html.j2")
