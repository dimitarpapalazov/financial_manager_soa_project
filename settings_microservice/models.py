from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import enum
from ..user_microservice.models import User


class Type(enum.Enum):
    expense = 0
    income = 1


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum(Type), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def to_csv():
        return '{},{},{},{}'.format(self.id, self.name, self.type, self.user_id)


class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    short_name = db.Column(db.String, nullable=False)
    value_to_eur = db.Column(db.Decimal, nullable=False)


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True


class CurrencySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Currency
        load_instance = True
