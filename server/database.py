from sqlalchemy import JSON, Column, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class JsonData(Base):
    __tablename__ = "json_data"
    id = Column(Integer, primary_key=True)
    entry = Column(JSON)


def setup_database():
    engine = create_engine("sqlite:///db.db", echo=True)
    Base.metadata.create_all(bind=engine)
    return engine


def create_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
