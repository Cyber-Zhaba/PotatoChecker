import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from db_session import SqlAlchemyBase


class Sites(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'sites'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ping = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    state = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ids_feedbacks = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    reports = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    moderated = sqlalchemy.Column(sqlalchemy.BOOLEAN)
