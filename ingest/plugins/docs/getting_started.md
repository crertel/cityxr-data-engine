# Getting Started With Plugins

**Running the Ingest Server**

In the terminal, from the City XR directory enter `bin/run_ingest.sh`. This checks for and installs the required dependencies, builds the database and begins running user plugins.

---

**Creating Plugins**

All plugins should be created within `user_data_sources` in the `ingest` folder. Any relevant files will be contained in `datasets`, also contained in `ingest`. Make sure when building your plugin you use the appropriate path to reach the dataset.


For plugins to work appropriately with the server, they will rely on a number of functions within the file.

Essential imports:
```
from apscheduler.triggers.interval import IntervalTrigger   //used for scheduling
import logging          //used to pass messages regarding status
```
Currently, we also support the following imports:
```
//For webscrapes:
import requests
from bs4 import BeautifulSoup

//For csv files:
import csv
from os.path import join, dirname, abspath
```
If your dataset involves dates, you will also want to import the `datetime` and `time` libraries.


There are also five functions that are necessary for proper plugin function:
```
schedule()
init()
get_fields()
fetch_data()
clean_data()
```

-   The `schedule()` function is where you will denote the frequency with which your plugin will run, with the additional option to start or end on a specific date. The `IntervalTrigger` function used for this purpose accepts the following arguments: `weeks`, `days`, `hours`, `minutes`, `seconds`, `start_date`, `end_date()`, and `timezone`. 
-   `init()` initializes the plugin. No changes should be made to this function.
-   `get_fields()` receives the field names for each data type in the source, as well as the type of data, to create the schema for the datasource. This function should return a dictionary, and can accept the following data types: `decimal`, `string`, `boolean`, `timestamp`, and `date`.
-   `fetch_data()` will contain the code to receive and sort the raw data. Using `for` statements, assign data to variables one row at a time, appending each row to a dictionary as you go. The function should return this dictionary at the end to pass the data into the database. A more in-depth explanation of this process can be found in our guides to creating CSV- and Web-based plugins.
-   `clean_data()` receives the raw data collected in the previous step, and allows you to clean it for easier parsing. Similar to `fetch_data()`, you will go through the data one row at a time, and return the completed dictionary at the end. Not all files will require cleaning, but still must pass through this function to be able to access the data appropriately.



For more information on building plugins, checkout our guides on building CSV- or Web-based dataset plugins.

---

**View the Datatables**

From the terminal, enter `bin/connect_to_db` to open the database. To view a specific table, use `Select * from <datasource>;` The datasource name should be in the format of `datasource_xxx.schemaName;`. When entering the command, hit `Tab` after "datasource" to see the list of datasource options available. Schema name options are `archive_clean`, `archive_raw`, `current_clean`, `current_raw`, `log`, and `runs`.

```
//Example:
# select * from datasource_cac797880afab020b1093980e2d323acba2d0542.current_raw;
```
