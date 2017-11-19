from os import getenv


from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import  Session


def prepare_base_and_session(sql_engine):
    engine = create_engine(getenv(sql_engine))
    base = automap_base()
    base.prepare(engine, reflect=True)
    session = Session(engine)
    return base, session


dest_base, dest_session = prepare_base_and_session('DEST_SQL_ENGINE')
source_base, source_session = prepare_base_and_session('SOURCE_SQL_ENGINE')
