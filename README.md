# Microservice for Search Index of Phone Numbers

This project is aimed to test phonenumbers normalization process and alembic database migration to add new colomn for normalized phonenumbers before using it in production.

Quickstart
----------


Run the following commands to install project locally:

```
    # to install dependancies:
    pipenv shell
    pipenv install


    # enter db pathes
    export DEST_SQL_ENGINE=/path/to/db
    export SOURCE_SQL_ENGINE=/path/to/db


    # run alembic migration for test destination db
    alembic upgrade head


    # run normalization process
    python phone_normalizer.py

```

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
