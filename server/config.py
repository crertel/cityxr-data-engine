from environs import Env

env = Env()
env.read_env()

DEBUG = env.bool("DEBUG")
PG_HOST = env("PG_HOST")
PG_USER = env("PG_USER")
PG_PASSWORD = env("PG_PASSWORD")
PG_DB = env("PG_DB")
PG_PORT = env.int("PG_PORT")

LISTEN_PORT = env.int("LISTEN_PORT")

PG_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
