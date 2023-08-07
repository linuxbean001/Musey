from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(
    'root', '', 'localhost', 'musey')
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()
# def get_db() -> Generator:   #new
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()
