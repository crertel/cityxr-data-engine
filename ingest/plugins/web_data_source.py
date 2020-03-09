from plugins.data_source import DataSource


class WebDataSource(DataSource):
    def __init__(self, runtime_id, name):
        super().__init__(runtime_id, name)
        print("Web data source created")

