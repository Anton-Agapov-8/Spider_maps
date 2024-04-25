import sqlalchemy
from .db_session import SqlAlchemyBase


class SpidersDescription(SqlAlchemyBase):
    __tablename__ = 'spiders_descriptions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    color = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Spider_type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        reslist = [self.id, self.picture, self.name]
        return ';, '.join(map(str, reslist))
