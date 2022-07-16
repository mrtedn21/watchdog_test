from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

engine = create_engine('sqlite+pysqlite:///lite.db', future=True)
Base = declarative_base(engine)
metadata_obj = MetaData()


class Flight(Base):
    __tablename__ = 'flight'
    id = Column(Integer, primary_key=True)
    file_name = Column(String(256))
    flt = Column(Integer)
    depdate = Column(Date)
    dep = Column(String)
