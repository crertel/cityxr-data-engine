from config import LISTEN_PORT, DEBUG, PG_URL
import psycopg2
import connexion


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

app = connexion.FlaskApp(__name__)
if DEBUG:
    app.app.jinja_env.auto_reload = True
    app.app.config["TEMPLATES_AUTO_RELOAD"] = True
app.add_api("cxr-server.yaml")
app.run(host="0.0.0.0", debug=DEBUG, port=LISTEN_PORT)
