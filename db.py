from os import getenv


from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    DateTime,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


if getenv('DEBUG_FLAG'):
    sql_str = getenv('DEV_DEST_SQL_STR')
else:
    sql_str = getenv('PROD_SQL_STR')


engine = create_engine(sql_str)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Order(Base):
    __tablename__ = 'orders'

    order_id = Column('id', Integer, primary_key=True, index=True)
    created = Column('created', DateTime)
    contact_phone = Column('contact_phone',  String(100))
    normalized_phone = Column(
        'normalized_phone', Numeric(15,0), nullable=True)

    def __repr__(self):
        if normalized_phone:
            phone = self.normalized_phone
        else:
            phone = self.contact_phone
        return 'order id={order_id}, created={created}, phone={phone}'.format(
            order_id=self.order_id,
            created=self.created,
            phone=self.contact_phone,
        )
