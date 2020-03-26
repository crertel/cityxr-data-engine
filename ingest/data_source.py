from time import sleep
import logging
import importlib.util

from datetime import datetime, timezone
from multiprocessing import Process, Pipe

from database_connection import DatabaseConnection

from uuid import uuid4

import traceback

log = logging.getLogger(__name__)


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
            module_path=module_path,
            parent_pipe=parent_pipe,
        )
        self.next_trigger_time = None

    def _start_process(self, name, runtime_id, module_path, parent_pipe):
        self._process = Process(
            target=DataSource.do_run,
            name=f"{name}_{runtime_id}",
            daemon=True,
            args=(name, runtime_id, module_path, parent_pipe),
        )
        self._process.start()

    def retstart(self):
        self._process.kill()
        (child_pipe, parent_pipe) = Pipe(duplex=True)
        self._child_pipe = child_pipe
        self._start_process(
            name=self.name,
            runtime_id=self.runtime_id,
            module_path=self.module_path,
            parent_pipe=parent_pipe,
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

    def do_run(name, runtime_id, module_path, parent_pipe):
        log.warning("loading from " + module_path)
        spec = importlib.util.spec_from_file_location(f"plugin_{name}", module_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        init = plugin_module.init
        schedule = plugin_module.schedule
        data_source_fields = plugin_module.get_fields()
        fetch_data = plugin_module.fetch_data
        clean_data = plugin_module.clean_data

        log.error(f"rid {runtime_id} name {name}")

        init(runtime_id, name)

        next_trigger_time = None
        last_trigger_time = None
        schedule_trigger = schedule()

        db_connection = DatabaseConnection(runtime_id)
        db_connection.conect_to_database()

        if not db_connection.check_if_schema_exists():
            db_connection.schema_setup(data_source_fields)

        # while <pump messages queue>:
        #
        log.error("started data source")
        while 1:
            # if we have messages from the main process, handle them
            while parent_pipe.poll() is True:
                msg = parent_pipe.recv()
                # TODO: handle state querying messages, whatever else

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
                db_connection.begin_run(run_id)
                db_connection.empty_current_raw_table()
                db_connection.empty_current_clean_table()
                try:
                    db_connection.update_run(run_id, "fetching")
                    raw_data = fetch_data(db_connection, run_id)
                    db_connection.insert_data_current_raw(run_id, raw_data)

                    db_connection.update_run(run_id, "cleaning")
                    clean_data = clean_data(db_connection, run_id, raw_data)
                    db_connection.insert_data_current_clean(run_id, clean_data)

                    db_connection.archive_raw()
                    db_connection.archive_clean()
                    run_succeeded = True
                except Exception as err:
                    db_connection.log(
                        time=datetime.now(timezone.utc),
                        severity="error",
                        message=traceback.format_exc(),
                        run_id=run_id,
                    )
                    log.error(err)
                    pass
                finally:
                    run_end_time = datetime.now(timezone.utc)
                    run_duration = run_end_time - run_start_time

                    # TODO record run statistics
                    if run_succeeded:
                        log.error(f"Run #{run_id} succeeded in #{run_duration}")
                        db_connection.end_run(run_id, "succeeded")
                    else:
                        log.error(f"Run #{run_id} failed in #{run_duration}")
                        db_connection.end_run(run_id, "failed")
            sleep(1)
