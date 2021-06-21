from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    gender = db.Column(db.String)
    age = db.Column(db.Integer)
    role = db.Column(db.String)
    verification_code = db.Column(db.String)
    is_verified = db.Column(db.Boolean)


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
