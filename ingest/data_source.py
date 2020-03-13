from enum import Enum
from time import sleep
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
    def __init__(self, source_code, runtime_id, name, module_path):
        self.runtime_id = runtime_id
        self.source_code = source_code
        self.name = name
        self.started_at = datetime.now(timezone.utc)
        self.module_path = module_path
        (child_pipe, parent_pipe) = Pipe(duplex=True)
        self._child_pipe = child_pipe
        self._start_process(
            name=name,
            runtime_id=runtime_id,
            parent_pipe=parent_pipe,
            module_path=module_path,
        )
        self.next_trigger_time = None

    def _start_process(self, name, runtime_id, parent_pipe, module_path):
        self._process = Process(
            target=DataSource.do_run,
            name=f"{name}_{runtime_id}",
            daemon=True,
            args=(name, runtime_id, parent_pipe, module_path,),
        )
        self._process.start()

    def retstart(self):
        self._process.kill()
        (child_pipe, parent_pipe) = Pipe(duplex=True)
        self._child_pipe = child_pipe
        self._start_process(
            name=self.name, runtime_id=self.runtime_id, module_path=self.module_path
        )

    def update(self):
        cpipe = self._child_pipe
        while cpipe.poll() is True:
            # TODO: for every parent message, pop it off and do something with it
            msg = (msg_type, msg_body) = cpipe.recv()

            if msg_type == "update_trigger_time":
                self.next_trigger_time = msg_body
            log.warning(msg)
            # handle state querying messages, whatever else

    def do_run(runtime_id, name, parent_pipe, module_path):
        log.warning("loading from " + module_path)
        spec = importlib.util.spec_from_file_location(f"plugin_{name}", module_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        init = plugin_module.init
        schedule = plugin_module.schedule
        migrate_if_needed = plugin_module.migrate_if_needed
        fetch_data = plugin_module.fetch_data
        clean_data = plugin_module.clean_data

        state = init(runtime_id, name)

        next_trigger_time = None
        last_trigger_time = None
        schedule_trigger = schedule()

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
                msg = parent_pipe.recv()
                # handle state querying messages, whatever else

            # after we handle pending events, if schedule says so we do a run.
            now = datetime.now(timezone.utc)
            if next_trigger_time is None or now >= next_trigger_time:
                next_trigger_time = schedule_trigger.get_next_fire_time(
                    last_trigger_time, now
                )
                parent_pipe.send(("update_trigger_time", next_trigger_time))

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
            sleep(1)
