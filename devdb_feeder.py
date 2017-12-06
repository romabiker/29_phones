from os import getenv
import time
import logging


from sqlalchemy import exc, func
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


def get_latest_order_datetime():
    return dest_session.query(func.max(dest_order_cls.created)).first()


def request_source_db(latest_datetime, tries=3, step=1):
    while True:
        try:
            return source_session.query(source_order_cls).filter(
                source_order_cls.created > latest_datetime).all()
        except exc.DBAPIError as error:
            tries -= step
            if not tries:
                logging.error('There is {error_msg}'.format(error_msg=error.msg))
                return None


def watch_source_db_and_feed_dest_db(latest_datetime, delay=2*60, first=0):
    while True:
        source_orders = request_source_db(latest_datetime)
        if source_orders is None:
            break
        orders_quantity = len(source_orders)
        logging.info('{quantity} orders have come'.format(quantity=orders_quantity))
        if orders_quantity:
            latest_datetime = source_orders[first].created
            logging.info('the latest order at {datetime}'.format(
                datetime=latest_datetime))
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
        logging.info('sleeping {delay} secs'.format(delay=delay))
        time.sleep(delay)


if __name__ == '__main__':
    latest_order_datetime = get_latest_order_datetime()
    watch_source_db_and_feed_dest_db(latest_order_datetime)
