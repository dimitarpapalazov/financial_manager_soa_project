from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..user_microservice.models import User


class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')


class AccountSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Account
        load_instance = True
