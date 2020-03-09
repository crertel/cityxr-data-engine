# import psycopg2
# try:
#     conn = psycopg2.connect(PG_URL)
#     c = conn.cursor()
#     c.execute("select 'hello, world!'")
#     rows = c.fetchall()
#     for r in rows:
#         print(r)

# except Exception as e:
#     print("I am unable to connect to the database:")
#     print(e)

from plugins.data_source import DataSource


class PostgresDataSource(DataSource):
    def __init__(self, runtime_id, name):
        super().__init__(runtime_id, name)
        print("Postgres data source created")

