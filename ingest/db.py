from config import PG_URL
import psycopg2
from pprint import pprint


def create_db_connection():
    db_connection = psycopg2.connect(PG_URL)
    return db_connection


def create_schema(db_connection, name):
    cursor = db_connection.cursor(db_connection)
    cursor.execute("select 'hello, world!'")
    cursor.commit()


def dump_table(db_connection, schema, table):
    cursor = db_connection.cursor(db_connection)
    cursor.execute(
        """
SELECT
   column_name,
   data_type,
FROM
   information_schema.COLUMNS
WHERE
   table_schema = %s and table_name = %s;
    """,
        (schema, table),
    )
    rows = cursor.fetchall()
    for r in rows:
        pprint(r)
