from __future__ import print_function
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users '
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.name


session = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def init_app(app):
    conf = 'sqlite:////tmp/test.db'
    app.config['DB'] = conf
    engine = create_engine(conf)
    session.configure(bind=engine)
    Base.query = session.query_property()


def init_db(app):
    conf = 'sqlite:////tmp/test.db'
    app.config['DB'] = conf
    engine = create_engine(conf)
    Base.metadata.create_all(bind=engine)
    print('init db successfully')
