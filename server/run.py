from app import app
from config import LISTEN_PORT, DEBUG, PG_URL
import psycopg2


db_conn = psycopg2.connect(PG_URL)
db_cursor = db_conn.cursor()
db_cursor.execute(
    """
create extension if not exists "uuid-ossp";
"""
)
db_conn.commit()
db_cursor.close()
db_conn.close()


if DEBUG:
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
app.run(host="0.0.0.0", debug=DEBUG, port=LISTEN_PORT)
