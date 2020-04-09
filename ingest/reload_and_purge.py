from flask import Flask
import psycopg2
from database_connection import DatabaseConnection
from data_source import DataSource

app = Flask(__name__)


def __init__(self, runtime_id):
    self.runtime_id = runtime_id

@app.route("/why")
def helloWorld()
    return("Hello World!")

@app.route("/plugins/<self.runtime_id>/purge_and_reload", methods=["POST"])
def restart_button(self.runtime_id):
    return "<form method='post' action='/reload/'><button type='submit' button class='danger'>RESET</button></form>"



# receive sourceid
# define app.route using sourceid
# POST reset button
# get paid
