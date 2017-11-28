# Microservice for Search Index of Phone Numbers

This project is aimed to test phonenumbers normalization script "phone_normalizer.py" and alembic database migration to add a new colomn for normalized phonenumbers.

In development script "devdb_feeder.py" is used to simulate orders feeding from production  to development database.

In production case only the script "phone_normalizer.py" is needed.


###Development:


```
    # to install dependancies:
    pipenv shell
    pipenv install


    # enter development sql strings
    export DEBUG_FLAG=1
    export DEV_DEST_SQL_STR=/sql/str/to/db
    export DEV_SOURCE_SQL_STR=/sql/str/to/db


    # add DEV_DEST_SQL_STR  as sqlalchemy.url to alembic.ini
    # and run database migration
    alembic upgrade head


    # run feeding for development
    python devdb_feeder.py


    # run normalization process
    python phone_normalizer.py

```

###Production:

```
    # to install dependancies:
    pipenv shell
    pipenv install


    # enter production sql string
    export DEBUG_FLAG=0
    export PROD_SQL_STR=/sql/str/to/db


    # add PROD_SQL_STR as sqlalchemy.url to alembic.ini
    # and run database migration
    alembic upgrade head


    # run normalization process
    python phone_normalizer.py

```



# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
