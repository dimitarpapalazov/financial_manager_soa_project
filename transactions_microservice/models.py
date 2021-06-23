from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from ..user_microservice.models import User
from ..settings_microservice.models import Category
from ..accounts_microservice.models import Account


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    account = db.relationship('Account')
    amount = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def to_csv():
        return '{},{},{},{},{},{},{}'.format(self.id, self.date, self.category_id, self.account_id, self.amount, self.description, self.user_id)


class TransactionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        load_instance = True
