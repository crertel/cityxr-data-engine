#City XR Data Project

We’ll develop a data engine package to handle ingestion and querying of data. This will consist of two programs and supporting scripts:

- The cxd-ingest program will run and continuously sample data according to its source plugins.
- The cxd-server program will run and serve queries over a some kind of GraphQL or RESTy interface for batch queries and also route real-time messages to data set subscribers via websockets.

## Assumptions

- The engine will use Postgres 11 as a backing data store.
- The engine will target deployment on Linux servers.
- Operators will have basic business analyst knowledge--e.g., ability to modify example stub scripts.

Data sources supported will be:

- SQL queries via ODBC
- Document fetching via HTTP
- JSON payloads received via HTTP POST
- Local filesystem access

Datasets will be one of:

- Point-in-time data (“These businesses are at these locations 12 days ago.”)
- Time-series data (“These locations had this temperature between May 5 and Nov 5.”)
- Instantaneous data (“This is the current value of water in this flood plain.”)

## Features

The overall engine features will:

- Thorough documentation of engine architecture.
- Tutorials for common engine use-cases.
- Helper scripts to generate stub data source plugins.
- Helper scripts to manage the engine.
- Instructions for deployment.

The cxd-ingest program will:

- Have a shell script for generating stub plugins to add data sources.
- Have a plugin architecture for supporting data sources as described above.
- Plugins will be written in Python 3.
- Plugins will register themselves with the ingest program and run their setup (creation of database tables, etc.).
- Plugins may either stay resident (if they need to receive webhooks) or schedule themselves for periodic servicing.
- When serviced, plugins will run in two parts:
  - A fetch phase, where they receive or gather their data.
  - An ingest phase, where they process and clean the data.
- Log errors and data quality conditions.

The cxd-server program will:

- Provide at least one of a RESTy or GraphQL interface for querying ingested data.
- Provide ability to retrieve batched data updates since some previous time (“Give me all new data since yesterday”).
- Provide periodic updates of data updates to clients subscribed to various datasets.
- Provide a maintenance/debugging interface to see what data sources are available, what data they have, what their run status is, and to visualize that data.
