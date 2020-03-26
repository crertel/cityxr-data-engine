from enum import Enum


class DataSourceState(Enum):
    starting = "starting"
    running = "running"
    paused = "paused"
    terminated = "terminated"
    errored = "errored"
    disabled = "disabled"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
