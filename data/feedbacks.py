import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Feedbacks(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'feedbacks'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)

    owner_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("users.id"))

    time = sqlalchemy.Column(sqlalchemy.DATETIME)
    
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
