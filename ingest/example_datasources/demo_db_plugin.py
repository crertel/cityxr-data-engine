from apscheduler.triggers.interval import IntervalTrigger
import logging
import psycopg2
from environs import Env
import psycopg2.extras

psycopg2.extras.register_uuid()

env = Env()
env.read_env()

PG_HOST = env("PG_HOST")
PG_USER = env("PG_USER")
PG_PASSWORD = env("PG_PASSWORD")
PG_DB = env("PG_DB")
PG_PORT = env.int("PG_PORT")
PG_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

log = logging.getLogger(__name__)
log.error(f"PG_URL {PG_URL}")


def schedule():
    """
    Every 60 seconds we'll check the database schemas.
    """
    return IntervalTrigger(seconds=10)


def init(runtime_id, name):
    """
    Intializes the data source.
    Returns the initial state of the data source.
    """
    return {}


def get_fields():
    return {"schema_name": "string", "time": "timestamp"}


def fetch_data(db_connection, run_id):
    """
    We connect to the database, query its schemas
    and the time we're querying it, and return that.
    """
    ret = []
    try:
        dbconn = psycopg2.connect(PG_URL)
        curs = dbconn.cursor()
        curs.execute(
            "select schema_name, now() as time from information_schema.schemata;"
        )
        dbconn.commit()
        data = curs.fetchall()
        for (schema_name, time) in data:
            ret.append({"schema_name": schema_name, "time": time})
    except Exception as e:
        log.error(e)
    finally:
        # we always want to free the connection afterwards to prevent spamming
        # the database.
        del dbconn
        return ret


def clean_data(db_connection, run_id, run_data):
    """
    We're going to ignore any schemas in our data that aren't datasource related.
    """
    clean_run_data = []
    for datapoint in run_data:
        if datapoint["schema_name"].startswith("datasource_"):
            clean_run_data.append(datapoint)
    return clean_run_data
