# database.py - db connection setup (SQLAlchemy engine & session)

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)  # To tell app where and how to connect to db
session = sessionmaker(autocommit=False,autoflush=True,bind=engine) # To connect to db

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()