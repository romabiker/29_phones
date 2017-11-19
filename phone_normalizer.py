from os import getenv
import time
import logging


import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from sqlalchemy import exc


from db import (
    dest_base,
    dest_session,
    source_base,
    source_session,
)


dest_order_cls = dest_base.classes.orders
source_order_cls = source_base.classes.orders
logging.basicConfig(level=logging.INFO, format='%(message)s')


def normalize_to_national_number(phonenumber, country='RU'):
    try:
        phonenumber_obj = phonenumbers.parse(phonenumber, country)
        return phonenumber_obj.national_number
    except NumberParseException:
        try:
            phonenumber_obj = phonenumbers.parse('+7{}'.format(phonenumber), country)
            return phonenumber_obj.national_number
        except NumberParseException:
            return None


def normalize_dest_db_and_get_latest_time(one=1):
    dest_orders = dest_session.query(dest_order_cls).order_by(dest_order_cls.created.desc())
    for order in dest_orders.all():
        if not order.normalized_phones:
            order.normalized_phones = normalize_to_national_number(
                                                          order.contact_phone)
            dest_session.add(order)
    latest_order = dest_orders.limit(one).first()
    dest_session.commit()
    return latest_order.created


def request_source_db(latest_date, tries=5, step=1):
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


def watch_source_db(latest_date, delay=5, first=0):
    while True:
        source_orders = request_source_db(latest_date)
        if source_orders is None:
            break
        orders_quantity = len(source_orders)
        logging.info('{quantity} orders have come'.format(quantity=orders_quantity))
        if not orders_quantity:
            logging.info('sleeping {delay}'.format(delay=delay))
            time.sleep(delay)
            continue
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
                normalized_phones=normalize_to_national_number(
                                  source_order.contact_phone),)
            dest_session.add(dest_order)
        dest_session.commit()
        logging.info('After commit sleeping {delay}'.format(delay=delay))
        time.sleep(delay)


if __name__ == '__main__':
    latest_order_datetime = normalize_dest_db_and_get_latest_time()
    watch_source_db(latest_order_datetime)
