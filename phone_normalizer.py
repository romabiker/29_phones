from os import getenv
import time
import logging


import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from sqlalchemy import exc


from db import session, Order


logging.basicConfig(level=logging.INFO, format='%(message)s')


def normalize_to_national_number(phonenumber, country='RU'):
    try:
        phonenumber_obj = phonenumbers.parse(phonenumber, country,)
    except NumberParseException:
        try:
            phonenumber_obj = phonenumbers.parse('+7{}'.format(phonenumber), country)
        except NumberParseException:
            return None
    return phonenumber_obj.national_number


def query_not_normalized_orders(delay=60, tries=5, step=1):
    while True:
        try:
            return session.query(Order).filter(
                Order.normalized_phone.is_(None)).all()
        except exc.DBAPIError as error:
            tries -= step
            if not tries:
                raise error
            time.sleep(delay)


def watch_prod_db(delay=2*60):
    while True:
        try:
            orders_to_normalize_phone = query_not_normalized_orders()
        except exc.DBAPIError as error:
            logging.error('{error_msg} happened while db connection'.format(
                error_msg=error.message))
            break
        orders_amount_to_norm = len(orders_to_normalize_phone)
        if orders_amount_to_norm:
            logging.info('{orders_amount_to_norm} orders to normalize'.format(
                orders_amount_to_norm=orders_amount_to_norm))
            for order in orders_to_normalize_phone:
                order.normalized_phone = normalize_to_national_number(
                                              order.contact_phone)
                session.add(order)
            session.commit()
        logging.info('sleeping {delay}'.format(delay=delay))
        time.sleep(delay)


if __name__ == '__main__':
    watch_prod_db()

