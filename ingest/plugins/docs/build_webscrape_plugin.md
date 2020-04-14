# Creating a Web-Based Plugin Using BeautifulSoup

Begin with your essential imports:
```
from apscheduler.triggers.interval import IntervalTrigger
from bs4 import BeautifulSoup
import from os.path import join, dirname, abspath
import logging
```
If your data includes dates or times, you will want to import utilities for those as well:
```
import time
from datetime import date
```

We will also need to declare several variables for functionality:
```
log = logging.getLogger(__name__)

script_path = abspath(__file__)
script_dir = dirname(script_path)
```

-   `log` will be used to send messages from the plugin (i.e. warnings, info, errors)
-   `script_dir` ensures that the data received is going to the correct place

---

**schedule()**

For scheduling purposes, we will be relying on the `IntervalTrigger()` function. Within the 
`schedule()` module, denote what frequency you would like your data pulled. The `IntervalTrigger()` function can accept the following parameters:
-   weeks (int)
-   days (int)
-   hours (int) 
-   minutes (int)
-   seconds (int)
-   start_date (datetime|str)
-   end_date (datetime|str)
-   timezone (datetime.tzinfo|str)

```
return IntervalTrigger(seconds=5)
```

---

**get_fields()**


Within `get_fields()` we will be telling the database what datatypes it will be receiving. Name your 
fields within a dictionary, and specify what each datatype is. Acceptable options are `decimal`, 
`string`, `boolean`, `timestamp`, or `date`.
```
return {"value1": "date", "value2": "decimal", "value3": "string"}
```

---

**fetch_data()**


The `fetch_data()` module is where your data will be fetched and inserted into the database. Once you've connected to your webpage, begin working row by row. For each row, insert each datapoint into a variable with the correct formatting. At the end of the row, append each datapoint into a dictionary, in the same order you declared them in the `get_fields()` module. Once the dictionary has received each row, return it to be entered into the database.

The `fetch_data()` module is where your data will be fetched and inserted into the database. Beging by creating a variable to connect to your targe webpage. Within the source code of the page, find the tag containing all of your data- you may need to use several variables to specify the exact location. 

```
page = requests.get("https://www.example.com/")
soup = BeautifulSoup(page.text, "html.parser")

items = []

table = soup.find(class_="ClassName")

for row in table.find_all("tr"):
    v1 = row.contents[1]
    v2 = row.contents[3]
    v3 = row.contents[5]
    items.append({
        "value1": v1.contents[0].strip(),
        "value2": v2.contents[0].strip(),
        "value3": v3.contents[0].strip(),
        })
return items
```

In this example, we would pull everything in the "ClassName" tag, and then from that pull each instance of the "tr" tag. We'll remove all outer tags as we receive each item, and make one more pass as they are appended to the dictionary to make sure there's no additional tags or whitespace.

---

**clean_data()**

Once all of the raw data has been received, the cleaning process can begin. Similar to the `fetch_data()` process, we will be receiving the data one row at a time, inserting into variables and appending to a dictionary. During this process is when any formatting or cleanup can be done. Once this has completed, return the data one final time.

