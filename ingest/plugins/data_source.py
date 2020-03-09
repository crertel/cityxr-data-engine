from enum import Enum
import logging
from abc import abstractmethod, ABCMeta

from datetime import datetime, timezone
from multiprocessing import Process, Pipe

from uuid import uuid4

log = logging.getLogger(__name__)


class DSState(Enum):
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


class DataSource(metaclass=ABCMeta):
    def __init__(self, runtime_id, name):
        self.runtime_id = runtime_id
        self.name = name
        self.started_at = datetime.now(timezone.utc)

        (child_pipe, parent_pipe) = Pipe(duplex=True)
        self._child_pipe = child_pipe
        self._process = Process(
            target=DataSource.do_run,
            name=f"{name}_{runtime_id}",
            daemon=True,
            args=(
                {
                    "state": DSState.starting,
                    "name": name,
                    "runtime_id": runtime_id,
                    "parent_pipe": parent_pipe,
                },
            ),
        )
        self._process.start()

    def do_run(args):
        migrate_if_needed = args["miigrate_if_needed"]
        fetch_data = args["fetch_data"]
        clean_data = args["clean_data"]

        # TODO <setup scheduler>

        # TODO <handle DB migrations via migrate_if_needed>
        # db_connection = <get the database connection>
        db_connection = None
        migrate_if_needed(db_connection)

        # while <pump messages queue>:
        #
        log.error("started data source")
        while 1:
            # if we have messages from the main process, handle them
            while parent_pipe.poll() is True:
                # TODO: for every parent message, pop it off and do something with it
                # msg = <recv one message from parent pipe>
                # handle state querying messages, whatever else
                pass

            # after we handle pending events, if schedule says so we do a run.
            # TODO: <only do this if the scheduler says it's time to
            run_id = uuid4()
            run_start_time = datetime.now(timezone.utc)
            run_succeeded = False
            try:
                raw_data = fetch_data(db_connection, run_id)
                clean_data(db_connection, run_id, raw_data)
                run_succeeded = True
            except:
                # TODO log errors
                pass
            finally:
                pass
                # TODO record run results

            # TODO: sleep some reasonable amount b/c schedule

    @abstractmethod
    def migrate_if_needed(db_connection):
        """
        Method called to check if the schema and tables for a data source exist in the DB.
        Does nothing if they do, creates them if they don't.
        """
        pass

    @abstractmethod
    def fetch_data(db_connection, run_id):
        """
        Method called to fetch the data for a run.
        Returns the data to be worked on.
        """
        pass

    @abstractmethod
    def clean_data(db_connection, run_id, run_data):
        """
        Method called to clean up the data for a run.
        Will insert the data from a run into the DB.
        """
        pass
