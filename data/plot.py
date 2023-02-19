import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Plot(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'plot'
    id_site = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("sites.id"),
                                primary_key=True)
    points = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    point_time = sqlalchemy.Column(sqlalchemy.String, nullable=True)
