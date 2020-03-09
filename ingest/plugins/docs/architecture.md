-   check to see if relative schema exists within database
-   if no, add self (i.e. do migrations)
-   set a schedule to run plugin
-   retrieve, clean, and insert data into appropriate database

    -   retrieve data in pieces, clean simultaneously?
        -   each step as independent process
        -   two cleaning passes: one to make data readable, one to clean data