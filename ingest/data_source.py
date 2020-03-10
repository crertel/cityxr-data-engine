from enum import Enum
import logging
import importlib.util

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


class DataSource:
    def __init__(self, runtime_id, name, module_path):
        self.runtime_id = runtime_id
        self.name = name
        self.started_at = datetime.now(timezone.utc)
        self.module_path = module_path
        (child_pipe, parent_pipe) = Pipe(duplex=True)
        self._child_pipe = child_pipe
        self._process = Process(
            target=DataSource.do_run,
            name=f"{name}_{runtime_id}",
            daemon=True,
            args=(name, runtime_id, parent_pipe, module_path,),
        )
        self._process.start()

    def do_run(runtime_id, name, parent_pipe, module_path):
        print("loading from " + module_path)
        spec = importlib.util.spec_from_file_location(f"plugin_{name}", module_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        init = plugin_module.init
        schedule = plugin_module.schedule
        migrate_if_needed = plugin_module.migrate_if_needed
        fetch_data = plugin_module.fetch_data
        clean_data = plugin_module.clean_data

        state = init(runtime_id, name)

        # TODO <setup scheduler>
        schedule = schedule()

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
