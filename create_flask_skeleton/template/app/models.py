from __future__ import print_function
from sqlalchemy.ext.declarative import declarative_base
from .globals import Model
import sqlalchemy as sa


Base = declarative_base()


class User(Model):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), unique=True)
    email = sa.Column(sa.String(120), unique=True)
    is_admin = sa.Column(sa.Boolean, default=False)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return "<User %r>" % self.name
