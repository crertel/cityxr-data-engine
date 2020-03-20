import psycopg2


class Database:
    def __init__(self, data_source_runtime_id):
        self.conn = psycopg2.connect(data_source_runtime_id)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    @property
    def connection(self):
        return self.conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def schema_setup(self, parameter_list, data_source_runtime_id):
        self.cursor.execute("DROP TABLE IF EXISTS %s", data_source_runtime_id)
        schema = {parameter_list}
        self.cursor.execute(
            """CREATE TABLE {0}({1})""".format(data_source_runtime_id, schema)
        )

    def log_message(self, data_source_runtime_id, time, message):
        messages = [data_source_runtime_id, time, message]
        self.conn.log(messages)
