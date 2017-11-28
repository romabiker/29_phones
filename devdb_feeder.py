from os import getenv
import time
import logging


from sqlalchemy import exc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def prepare_orders_cls_and_session(sql_str):
    engine = create_engine(getenv(sql_str))
    base = automap_base()
    base.prepare(engine, reflect=True)
    orders_cls = base.classes.orders
    session = Session(engine)
    return orders_cls, session


dest_order_cls, dest_session = prepare_orders_cls_and_session('DEV_DEST_SQL_STR')
source_order_cls, source_session = prepare_orders_cls_and_session('DEV_SOURCE_SQL_STR')
logging.basicConfig(level=logging.INFO, format='%(message)s')


def get_latest_order_time(one=1):
    dest_orders = dest_session.query(
        dest_order_cls).order_by(dest_order_cls.created.desc())
    latest_order = dest_orders.limit(one).first()
    return latest_order.created


def request_source_db(latest_date, tries=3, step=1):
    while True:
        try:
            return source_session.query(source_order_cls).order_by(
                source_order_cls.created.desc()).filter(
                source_order_cls.created > latest_date).all()
        except exc.DBAPIError as error:
            tries -= step
            if not tries:
                logging.error('There is {error_msg}'.format(error_msg=error.msg))
                return None


def watch_source_db_and_feed_dest_db(latest_date, delay=2*60, first=0):
    while True:
        source_orders = request_source_db(latest_date)
        if source_orders is None:
            break
        orders_quantity = len(source_orders)
        logging.info('{quantity} orders have come'.format(quantity=orders_quantity))
        if not orders_quantity:
            logging.info('sleeping {delay}'.format(delay=delay))
            time.sleep(delay)
        else:
            latest_date = source_orders[first].created
            logging.info('the latest order at {date}'.format(date=latest_date))
            for source_order in source_orders:
                dest_order = dest_order_cls(
                    id=source_order.id,
                    contact_phone=source_order.contact_phone,
                    contact_name=source_order.contact_name,
                    contact_email=source_order.contact_email,
                    status=source_order.status,
                    created=source_order.created,
                    confirmed=source_order.confirmed,
                    comment=source_order.comment,
                    price=source_order.price,
                )
                dest_session.add(dest_order)
            dest_session.commit()
            logging.info('After commit sleeping {delay}'.format(delay=delay))
            time.sleep(delay)


if __name__ == '__main__':
    latest_order_datetime = get_latest_order_time()
    watch_source_db_and_feed_dest_db(latest_order_datetime)
