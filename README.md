Overview
--------
This project's been done with help of `Pipenve` on `Flask` framework.  
I've spend 3 days on learning `Python`, `Flask` and implementing the application based on the requested tasks.  

####Things to note
- Separating `DB.py`, `Helper.py` and `Validator.py` in to different files and folder (/core) was just a personal preferences, to make them more readable, organized and prevention of spaghetti-coding. 
- Currency codes and abbreviations for purpose of validation have been extracted from [https://openexchangerates.org/api/currencies.json](https://openexchangerates.org/api/currencies.json) and saved in to `currencies.json` file. Implementing the app in a way to read the currencies on-the-fly from an external API was also possible, but unnecessary since they almost never change.
- Since the application's been stated in the [POST requirements](https://github.com/xeneta/ratestask#post-requirements) to ask for two dates, the insert process is designed to upload multi records in to the database based on the dates range from `date_from` to `date_to`. I might have misunderstood this task or there might be a type in that part of the assignment. Regardless, if the application should insert just one record, please make sure `date_from`
and `date_to` are holding a same value.
- Up on inserting a record in to the _prices_ table, any given and/or converted (to USD) price would be rounded from decimal in to an integer. Since the _price_ column is designed to hold integer.

####App Features
- Application can validate user input, and display error accordingly in json format. It can validate:
    - If required input is empty (empty `string`, `space`/`tab` or `None`)
    - If required input is a valid date (default format `YYYY-MM-DD`)
    - If required inputs (start date and end date) are a valid date range
    - If required input is a valid currency code
    - If required input is exists in database (e.g. port code)
    - If required input is a number
- Any connection to the database would be closed, once the query's been executed or a database connection exception is raised.
- Errors with code `404` (Not Found) and `500` (Internal Server Error) are converted to be displayed in json format.
- All of the internal server errors will be logged in a `log.txt` file located on the root of the project      

 
Initial setup  
-------------
This project was created and tested `Python 3.7`.   
- Install `Pipenv` following [this instruction](https://docs.pipenv.org/en/latest/#install-pipenv-today) and then run these commands in your terminal application:
```bash
$ cd <project root directory>
$ pipenv shell
```
- and then install libraries below with `pipenv install <library>` command, and make sure they are at least on the following version  

    - flask = 1.0.3
    - psycopg2-binary = 2.8.3
    - requests = 2.22.0  
    
- Next set the `PostgreSQL` database config url and [https://openexchangerates.org/api]([https://openexchangerates.org/api) app id as **Environment Variables** with the following keys:
``` bash
$ export DATABASE_URL="postgresql://user@host/db"
$ export OPEN_EXCHANGE_APP_ID=<APP ID>
```
- Finally run the `app.py`, the application should be listening for requests on `http://127.0.0.1:5000/`.

Usage 
-----
####Endpoints (Tasks)
#####GET
- Implemented an API endpoint that returns a list with the average prices for each day on a route between Port Codes origin and destination. 
```
http://127.0.0.1:5000/rates/
    ? date_from     = required|should be a valid date (YYYY-MM-DD)|should be equal or less than date_to
    & date_to       = required|should be a valid date (YYYY-MM-DD)|should be equal or greater than date_from
    & origin        = required
    & destination   = required
```
- Implemented an API endpoint that return an empty value (JSON null) for days on which there are less than 3 prices in total.
```
http://127.0.0.1:5000/rates_null/
    ? date_from     = required|should be a valid date (YYYY-MM-DD)|should be equal or less than date_to
    & date_to       = required|should be a valid date (YYYY-MM-DD)|should be equal or greater than date_from
    & origin        = required
    & destination   = required
```
  
#####POST
- Implemented an API endpoint where you can upload a price with optional currency code.
```
http://127.0.0.1:5000/rates/
    ? date_from     = required|should be a valid date (YYYY-MM-DD)|should be equal or less than date_to
    & date_to       = required|should be a valid date (YYYY-MM-DD)|should be equal or greater than date_from
    & origin        = required|should exists in the _ports_, column _code_
    & destination   = required|should exists in the _ports_, column _code_
    & price         = required|should be a number
    & currency      = not required if the key _currency_ is not mentioned|should be a valid currency code
```

Batch processing 
----------------
#####Problem
I have personally experienced such a scenario, and I must say no matter how big the database is on the resources, a lot of records would be lost. The database server would crash or on the best case it'll freeze and would not respond until all of the jobs in its own queue are done.
#####Solution
I would suggest to have a queue server such as RabitMQ or Redis Server to queue all of the incoming jobs before dispatching them directly to the main database.
This is well known pattern for handling large tasks at the back-end of an application. Depending on the language and application framework there are a number of queue implementations out there.
In this way group of worker processes in the background read the jobs off the queue and execute them. So any given job no matter how big it is, would not be lost and the database server is always on its normal stable state.
These type of servers also support persistent messaging so that jobs on a queue are recovered in the event of a failure.
