# models.py - SQLAlchemy ORM models (tables)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, String, Float, JSON 


Base = declarative_base() # Instantiate base class

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    price = Column(Float)
    discount_percentage = Column(Float)
    rating = Column(Float)
    stock = Column(Integer)
    brand = Column(String)
    sku = Column(String)
    weight = Column(Float)
    warranty_information = Column(String)
    shipping_information = Column(String)
    availability_status = Column(String)
    return_policy = Column(String)
    minimum_order_quantity = Column(Integer)
    thumbnail = Column(String)

    dimensions = Column(JSON)  # {width, height, depth}
    meta = Column(JSON)        # {createdAt, updatedAt, barcode, qrCode}
    reviews = Column(JSON)     # List of review objects
    tags = Column(JSON)        # List of strings
    images = Column(JSON)      # List of URLs