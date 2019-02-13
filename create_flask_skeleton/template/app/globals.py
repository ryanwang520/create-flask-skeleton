from flask import g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .db import ModelClass, Query
from sqlalchemy.orm import Session
from typing import TYPE_CHECKING

db = SQLAlchemy(model_class=ModelClass, query_class=Query)


session: Session = db.session

if TYPE_CHECKING:
    from .models import User

    class Model(ModelClass):
        pass


else:
    Model = db.Model


migrate = Migrate()


def current_user() -> "User":
    return g.user  # type: ignore
