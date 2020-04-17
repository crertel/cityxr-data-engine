import os
from superset.config import *
from werkzeug.contrib.cache import RedisCache


def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)


SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(DATA_DIR, "superset.db")

REDIS_HOST = ""
REDIS_PORT = ""
RESULTS_BACKEND = None


class CeleryConfig(object):
    BROKER_URL = (
        "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT),
        "sqla+sqlite:///" + os.path.join(DATA_DIR, "celeryDB.db"),
    )[bool(not REDIS_HOST)]
    CELERY_RESULT_BACKEND = (
        "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT),
        "db+sqlite:///" + os.path.join(DATA_DIR, "celeryResultDB.db"),
    )[bool(not REDIS_HOST)]
    CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"}}
    CELERY_IMPORTS = ("superset.sql_lab",)
    CELERY_TASK_PROTOCOL = 1


CELERY_CONFIG = CeleryConfig
