from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
import time

from app.db_config import DATABASE_URL
try:
    engine = create_engine(DATABASE_URL, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
except OperationalError:
    print("Database connection failed. Retrying in 3s...")
    time.sleep(3)
    

Base = declarative_base()