from time import sleep
import logging
import importlib.util

from datetime import datetime, timezone
from multiprocessing import Process, Pipe

from database_connection import DatabaseConnection

from uuid import uuid4

import traceback

log = logging.getLogger(__name__)
from pprint import pformat


class DataSource:
    def __init__(self, source_code, runtime_id, name, module_path):
        self.runtime_id = runtime_id
        self.source_code = source_code
        self.name = name
        self.status = "created"
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

    def retstart(self, purge_data=False):
        self._process.kill()
        if purge_data:
            dbc = DatabaseConnection(self.runtime_id)
            dbc.connect_to_database()
            dbc.purge_datasource_schema()
            dbc.disconnect_from_database()
        (child_pipe, parent_pipe) = Pipe(duplex=True)
        self._child_pipe = child_pipe
        self._start_process(
            name=self.name,
            runtime_id=self.runtime_id,
            module_path=self.module_path,
            parent_pipe=parent_pipe,
        )

    def pause(self):
        self.send_message("pause", "")

    def unpause(self):
        self.send_message("unpause", "")

    def ingest(self, msg_body):
        self.send_message("msg_ingest", msg_body)

    def send_message(self, msg_type, msg_body):
        self._child_pipe.send((msg_type, msg_body))

    def update(self):
        while self._child_pipe.poll() is True:
            (msg_type, msg_body) = self._child_pipe.recv()

            if msg_type == "update_trigger_time":
                self.next_trigger_time = msg_body
            elif msg_type == "update_status":
                self.status = msg_body

    def do_run(name, runtime_id, module_path, parent_pipe):
        spec = importlib.util.spec_from_file_location(f"plugin_{name}", module_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        init = plugin_module.init
        schedule = plugin_module.schedule
        if schedule() is None:
            ingest_data = plugin_module.ingest_data

        data_source_fields = plugin_module.get_fields()
        fetch_data = plugin_module.fetch_data
        clean_data = plugin_module.clean_data

        init(runtime_id, name)

        is_paused = False
        next_trigger_time = None
        last_trigger_time = None
        schedule_trigger = schedule()

        def message_parent(topic, msg):
            parent_pipe.send((topic, msg))

        def tell_parent_status(status):
            parent_pipe.send(("update_status", status))

        db_connection = DatabaseConnection(runtime_id)
        db_connection.connect_to_database()

        if not db_connection.check_if_schema_exists():
            db_connection.schema_setup(data_source_fields)

        while 1:
            # if we have messages from the main process, handle them
            ingests = []
            while parent_pipe.poll() is True:
                msg = (msg_type, msg_body) = parent_pipe.recv()
                if msg_type == "msg_ingest":
                    log.error(f"INGEST: {pformat(msg)}")
                    ingests.append(msg_body)
                elif msg_type == "pause":
                    log.error(f"PAUSED")
                    is_paused = True
                elif msg_type == "unpause":
                    log.error(f"UNPAUSED")
                    is_paused = False
                else:
                    log.error(f"MSG RECV: {pformat(msg)}")

            # after we handle pending events, if schedule says so we do a run.
            now = datetime.now(timezone.utc)
            if (schedule_trigger is None and len(ingests) > 0) or (
                schedule_trigger is not None
                and (next_trigger_time is None or now >= next_trigger_time)
            ):
                if schedule_trigger is not None:
                    next_trigger_time = schedule_trigger.get_next_fire_time(
                        last_trigger_time, now
                    )
                    message_parent("update_trigger_time", next_trigger_time)

                run_id = uuid4()
                run_start_time = datetime.now(timezone.utc)
                run_succeeded = False
                if is_paused:
                    tell_parent_status("paused")
                    continue
                else:
                    tell_parent_status("running")
                db_connection.begin_run(run_id)
                db_connection.empty_current_raw_table()
                db_connection.empty_current_clean_table()
                try:
                    db_connection.log(
                        time=datetime.now(timezone.utc),
                        severity="info",
                        message="started run",
                        run_id=run_id,
                    )
                    db_connection.update_run(run_id, "fetching")
                    if schedule_trigger is None:
                        raw_data = ingest_data(db_connection, run_id, ingests)
                    else:
                        raw_data = fetch_data(db_connection, run_id)
                    db_connection.insert_data_current_raw(run_id, raw_data)

                    db_connection.update_run(run_id, "cleaning")
                    cleaned_data = clean_data(db_connection, run_id, raw_data)
                    db_connection.insert_data_current_clean(run_id, cleaned_data)

                    db_connection.archive_raw()
                    db_connection.archive_clean()
                    db_connection.log(
                        time=datetime.now(timezone.utc),
                        severity="info",
                        message="finished run",
                        run_id=run_id,
                    )
                    run_succeeded = True
                except Exception as err:
                    db_connection.log(
                        time=datetime.now(timezone.utc),
                        severity="error",
                        message=traceback.format_exc(),
                        run_id=run_id,
                    )
                    log.error(traceback.format_exc())
                    pass
                finally:
                    run_end_time = datetime.now(timezone.utc)
                    run_duration = run_end_time - run_start_time

                    if run_succeeded:
                        log.error(f"Run #{run_id} succeeded in #{run_duration}")
                        db_connection.end_run(run_id, "succeeded")
                    else:
                        log.error(f"Run #{run_id} failed in #{run_duration}")
                        db_connection.end_run(run_id, "failed")
                tell_parent_status("sleeping")
            sleep(1)
