import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Spiders(SqlAlchemyBase):
    __tablename__ = 'spiders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    points = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        reslist = [self.id, self.name]
        return '; '.join(map(str, reslist))
