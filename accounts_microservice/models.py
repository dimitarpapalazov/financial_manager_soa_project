from app import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def to_csv():
        return '{},{},{},{},{}'.format(self.id, self.group, self.name, self.amount, self.user_id)


class AccountSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Account
        load_instance = True
