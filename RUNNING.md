# Installation and Operation

## Prerequisities

Make sure you have the following tools installed:

* Bash
* Docker >= 19.03 or compatible
* Docker compose >= 1.21.0

## Running the data ingest pipeline

1. Open a terminal to the root of the project.
2. Make sure that any user scripts you'd like the ingest server to run are copied into the `user_datasources` directory. Starter scripts to modify are in `example_datasources`.
3. Run `bin/start_ingest.sh`

A maintenance and monitoring web page will be available at `localhost:5001` by default, which lets you view the datasources that are running, pause them, unpause them, check run history, and check logs.

## Running the data server

1. Open a terminal to the root of the project.
2. Run `bin/start_server.sh`

Once running, this will server an OpenAPI/Swagger UI at `localhost:5002/v1/ui` by default.

## Connecting to the database

1. Open a terminal to the root of the project.
2. Run `bin/connect_to_db.sh`.

# Troubleshooting

**I can't bind to port 5001 or 5002!**

This is caused by there being an application running on the host machine on those ports. Try finding and closing that application, or alternately you can change the listening port in the dockerfiles.

**I can't see any datasources running!**

This may be due to not having a `ingest/user_datasources` folder with appropriate datasources. Prepopulate that with your datasources before running the server.

