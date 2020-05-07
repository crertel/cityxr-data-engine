def schedule():
    """
    We return "None" to signify we'll just listen for web hooks.
    """
    return None


def init(runtime_id, name):
    """
    Intializes the data source.
    Returns the initial state of the data source.
    """
    return {}


def get_fields():
    return {"a": "decimal"}


def fetch_data(db_connection, run_id):
    """
    Fetches the data for a run.
    Will insert data along with run into the DB.
    """
    return []


def ingest_data(db_connection, run_id, ingests):
    """
    Fetches the data for a run.
    Will insert data along with run into the DB.
    """
    return ingests


def clean_data(db_connection, run_id, run_data):
    """
    Cleans up the data for a run.
    Will insert the data from a run into the DB.
    """
    return run_data
