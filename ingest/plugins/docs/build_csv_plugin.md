# Creating a CSV-Based Plugin

Begin with your essential imports:

```python
from apscheduler.triggers.interval import IntervalTrigger
import csv
import from os.path import join, dirname, abspath
import logging
```

If your data includes dates or times, you will want to import utitilies for those as well:

```python
import time
from datetime import date
```

We will also need to declare several variables for functionality:

```python
log = logging.getLogger(__name__)

script_path = abspath(__file__)
script_dir = dirname(script_path)
```

- `log` will be used to send messages from the plugin (i.e. warnings, info, errors)
- `script_dir` ensures that the data received is going to the correct place

---

**schedule()**

For scheduling purposes, we will be relying on the `IntervalTrigger()` function. Within the
`schedule()` module, denote what frequency you would like your data pulled. The `IntervalTrigger()` function can accept the following parameters:

- weeks (int)
- days (int)
- hours (int)
- minutes (int)
- seconds (int)
- start_date (datetime|str)
- end_date (datetime|str)
- timezone (datetime.tzinfo|str)

```python
return IntervalTrigger(seconds=5)
```

---

**get_fields()**

Within `get_fields()` we will be telling the database what datatypes it will be receiving. Name your
fields within a dictionary, and specify what each datatype is. Acceptable options are `decimal`,
`string`, `boolean`, `timestamp`, or `date`.

```python
return {"value1": "date", "value2": "decimal", "value3": "string"}
```

---

**fetch_data()**

The `fetch_data()` module is where your data will be fetched and inserted into the database. With your csv file open, begin working row by row. For each row, insert each datapoint into a variable with the correct formatting. At the end of the row, append each datapoint into a dictionary, in the same order you declared them in the `get_fields()` module. Once the dictionary has received each row, return it to be entered into the database.

```python
items = []
    csv_path = join(script_dir, "../datasets/filename.csv")
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            pdate = time.strptime(row[0], "%d/%m/%Y")
            v1 = date(year=pdate.tm_year, month=pdate.tm_mon, day=pdate.tm_mday)
            v2 = float(row[1])
            v3 = row[3]
            items.append({"value1": v1, "value2": v2, "value3": v3})
    return items
```

Note that dates require an additional step- first we receive the data from the file appropriately, and then format it into a way the database can understand.

---

**clean_data()**

<<<<<<< HEAD:ingest/plugins/docs/build_csv_plugin.md
Once all of the raw data has been received, the cleaning process can begin. Similar to the `fetch_data()` process, we will be receiving the data one row at a time, inserting into variables and appending to a dictionary. During this process is when any formatting or cleanup can be done. Once this has completed, return the data one final time.

=======
`¯\_(ツ)_/¯`
>>>>>>> master:ingest/user_data_sources/build_csv_plugin.md
