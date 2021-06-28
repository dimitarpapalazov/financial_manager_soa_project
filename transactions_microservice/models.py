from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, nullable=False)
    account_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.String)
    user_id = db.Column(db.Integer, nullable=False)

    def to_csv():
        return '{},{},{},{},{},{},{}'.format(self.id, self.date, self.category_id, self.account_id, self.amount, self.description, self.user_id)


class TransactionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        load_instance = True
