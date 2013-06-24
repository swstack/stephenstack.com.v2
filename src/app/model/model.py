from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative.api import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    cups_of_coffee = Column(Integer)

    def __repr__(self):
        return "<User('%s','%s')>" % (self.username, self.password)
