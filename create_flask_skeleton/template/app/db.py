import datetime
from types import GeneratorType
from typing import List, Any, Optional, TypeVar, Type, Dict, Tuple, cast

import flask_sqlalchemy
from sqlalchemy.orm import load_only


from sqlalchemy import desc, Column, DateTime, ForeignKey, Integer, inspect
from sqlalchemy.ext.declarative import declared_attr
from flask_sqlalchemy import Pagination
from .api import NotFound


T = TypeVar("T", bound="ModelClass")


class ModelClass(flask_sqlalchemy.Model):
    query: "Query"
    EXCLUDED_FIELDS: Tuple[str] = cast(Tuple[str], ())

    @declared_attr
    def id(cls):
        for base in cls.__mro__[1:-1]:
            if getattr(base, "__table__", None) is not None:
                type = ForeignKey(base.id)
                break
        else:
            type = Integer

        return Column(type, primary_key=True)

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    @classmethod
    def mget(cls: Type[T], ids, fields=None) -> List[T]:

        if isinstance(ids, GeneratorType):
            raise TypeError(
                "mget not support generator as we cannot know the item size of this"
                " generator before consume it, actually we should know if it is empty"
                " to avoid empty id list query"
            )
        if not ids:
            return []
        q = cls.query
        if fields:
            q = q.options(load_only(*fields))
        ids = [int(id) for id in ids]
        result = q.filter(cls.id.in_(ids)).all()
        result = {r.id: r for r in result}
        return [result.get(i) for i in ids]

    def as_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
            if c.key not in self.EXCLUDED_FIELDS
        }

    @classmethod
    def serialize_list(cls, array):
        return [_.as_dict() for _ in array]

    @classmethod
    def add(cls, **kwargs):
        from .globals import session

        model = cls(**kwargs)
        session.add(model)
        return model

    def delete(self):
        from .globals import session

        session.delete(self)

    @classmethod
    def last(cls: Type[T]) -> Optional[T]:
        return cls.query.order_by(cls.id.desc()).first()  # type: ignore

    @classmethod
    def first(cls: Type[T]) -> Optional[T]:
        return cls.query.first()  # type: ignore

    def update_from_dict(self, obj: Dict[str, Any], *fields: str):
        def safe_setattr(k, v):
            if k not in self.columns:
                raise TypeError(f"{k} is not a valid column attribute")
            setattr(self, k, v)

        if not fields:
            for k, v in obj.items():
                safe_setattr(k, v)
        else:
            for field in fields:
                safe_setattr(field, obj[field])

    @property
    def columns(self):
        return inspect(self).mapper.column_attrs

    @classmethod
    def from_dict(cls: Type[T], obj, *fields) -> T:
        model = cls()
        model.update_from_dict(obj, *fields)
        return model

    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.query.filter(*args, **kwargs)

    @classmethod
    def filter_by(cls, **kwargs):
        return cls.query.filter_by(**kwargs)

    @classmethod
    def find_first(cls: Type[T], *args, **kwargs) -> Optional[T]:
        return cls.query.filter(*args, **kwargs).first()  # type: ignore

    @classmethod
    def find_one(cls: Type[T], *args, **kwargs) -> T:
        return cls.query.filter(*args, **kwargs).one()  # type: ignore

    @classmethod
    def find_by_one(cls: Type[T], *args, **kwargs) -> T:
        return cls.query.filter_by(*args, **kwargs).one()  # type: ignore

    @classmethod
    def find_one_or_404(cls: Type[T], *args, message=None, **kwargs) -> T:
        return cls.query.filter(*args, **kwargs).one_or_404(message)  # type: ignore

    @classmethod
    def find_one_or_none(cls: Type[T], *args, **kwargs) -> Optional[T]:
        return cls.query.filter(*args, **kwargs).one_or_none()  # type: ignore

    @classmethod
    def find(cls: Type[T], *args, **kwargs) -> List[T]:
        return cls.query.filter(*args, **kwargs).all()  # type: ignore

    @classmethod
    def find_by(cls: Type[T], *args, **kwargs) -> List[T]:
        return cls.query.filter_by(*args, **kwargs).all()  # type: ignore

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        return cls.query.all()  # type: ignore

    @classmethod
    def get(cls: Type[T], *args, **kwargs) -> Optional[T]:
        return cls.query.get(*args, **kwargs)  # type: ignore

    @classmethod
    def get_or_404(cls: Type[T], *args, **kwargs) -> T:
        return cls.query.get_or_404(*args, **kwargs)  # type: ignore


class Query(flask_sqlalchemy.BaseQuery):
    def paginate(
        self, page=None, per_page=None, error_out=False, max_per_page=None
    ) -> Pagination:
        return super().paginate(page, per_page, error_out, max_per_page)

    def id_desc(self) -> "Query":
        return self.order_by(desc("id"))  # type: ignore

    def created_at_desc(self):
        return self.order_by(desc("created_at"))

    def one_or_404(self, message=None):
        rv = self.one_or_none()
        if rv is None:
            raise NotFound(message)
        return rv

    def get_or_404(self, ident, message=None):

        rv = self.get(ident)
        if rv is None:
            raise NotFound(message)
        return rv

    def first_or_404(self, message=None):

        rv = self.first()
        if rv is None:
            raise NotFound(message)
        return rv
