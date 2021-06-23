from settings_microservice.models import Category
import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from ..user_microservice.models import User
from datetime import datetime, timedelta
from ..settings_microservice.app import db as settings_db
from calendar import monthrange


# Authorization configuration

def has_role(arg):
    def has_role_inner(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                headers = request.headers
                if 'AUTHORIZATION' in headers:
                    token = headers['AUTHORIZATION'].split(' ')[1]
                    decoded_token = decode_token(token)
                    if 'admin' in decoded_token['roles']:
                        return fn(*args, **kwargs)
                    for role in arg:
                        if role in decoded_token['roles']:
                            return fn(*args, **kwargs)
                    abort(401)
                return fn(*args, **kwargs)
            except Exception as e:
                abort(401)
        return decorated_view
    return has_role_inner


def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])


# Endpoints

def create(transaction_body):
  found_user = db.session.query(User).get(transaction_body['user_id'])
  if not found_user:
    new_transaction = Transaction(date=datetime.now(),
                          category_id=transaction_body['category_id'],
                          account_id=transaction_body['account_id'],
                          amount=transaction_body['amount'],
                          description=transaction_body['description'],
                          user_id=transaction_body['user_id'])
    db.session.add(new_transaction)
    db.session.commit()
    return transaction_schema.dump(new_transaction)
  else:
    return 404
  

def get(transaction_id):
  found_transaction = db.session.query(Transaction).get(transaction_id)
  if found_transaction:
    return transaction_schema.dump(found_transaction)
  else:
    return 404


def get_daily(get_body):
  found_user = db.session.query(User).get(get_body['user_id'])
  if found_user:
    transactions = db.session.query(Transaction).filter(
        user_id == get_body['user_id'], date == get_body['date']).all()
    if get_body['type'] != -1:
      categories = settings_db.session.query(Category).filter(type==get_body['type']).all()
      categories = (category.id for category in categories)
      for i in range(len(transactions)):
        if transactions[i].category_id not in categories:
          transactions.pop(i)
    if get_body['to_JSON']:
      return transaction_schema.dump(transactions, many=True)
    else:
      return transactions
  else:
    return 404


def get_weekly(get_body):
  found_user=db.session.query(User).get(get_body['user_id'])
  if found_user:
    date = get_body['date']
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    transactions = db.session.query(Transaction).filter(
        user_id == get_body['user_id'], date >= start, date <= end).all()
    if get_body['type'] != -1:
      categories = settings_db.session.query(
          Category).filter(type == get_body['type']).all()
      categories = (category.id for category in categories)
      for i in range(len(transactions)):
        if transactions[i].category_id not in categories:
          transactions.pop(i)
    if get_body['to_JSON']:
      return transaction_schema.dump(transactions, many=True)
    else:
      return transactions
  else:
    return 404


def get_monthly(get_body):
  found_user = db.session.query(User).get(get_body['user_id'])
  if found_user:
    date = get_body['date']
    start = date - timedelta(days=date.day - 1)
    month, days = monthrange(date.year, date.month)
    end = start + timedelta(days=days - 1)
    transactions = db.session.query(Transaction).filter(
        user_id == get_body['user_id'], date >= start, date <= end).all()
    if get_body['type'] != -1:
      categories = settings_db.session.query(
          Category).filter(type == get_body['type']).all()
      categories = (category.id for category in categories)
      for i in range(len(transactions)):
        if transactions[i].category_id not in categories:
          transactions.pop(i)
    if get_body['to_JSON']:
      return transaction_schema.dump(transactions, many=True)
    else:
      return transactions
  else:
    return 404


def get_annually(get_body):
  found_user = db.session.query(User).get(get_body['user_id'])
  if found_user:
    date = get_body['date']
    day_of_year = date.timetuple().tm_yday
    start = date - timedelta(days=day_of_year - 1)
    month, days = monthrange(date.year, 2)
    end = start + timedelta(days=366) if days == 29 else start + timedelta(days=365)
    transactions = db.session.query(Transaction).filter(
        user_id == get_body['user_id'], date >= start, date <= end).all()
    if get_body['type'] != -1:
      categories = settings_db.session.query(
          Category).filter(type == get_body['type']).all()
      categories = (category.id for category in categories)
      for i in range(len(transactions)):
        if transactions[i].category_id not in categories:
          transactions.pop(i)
    if get_body['to_JSON']:
      return transaction_schema.dump(transactions, many=True)
    else:
      return transactions
  else:
    return 404


def get_period(period_body):
  found_user = db.session.query(User).get(period_body['user_id'])
  if found_user:
    transactions = db.session.query(Transaction).filter(
        user_id == get_body['user_id'], date >= get_body['start'], date <= get_body['end']).all()
    if period_body['type'] != -1:
      categories = settings_db.session.query(
          Category).filter(type == period_body['type']).all()
      categories = (category.id for category in categories)
      for i in range(len(transactions)):
        if transactions[i].category_id not in categories:
          transactions.pop(i)
    if period_body['to_JSON']:
      return transaction_schema.dump(transactions, many=True)
    else:
      return transactions
  else:
    return 404


def update_date(date_body):
  found_transaction = db.session.query(
      Transaction).get(date_body['transaction_id'])
  if found_transaction:
    found_transaction.date = date_body['date']
    db.session.commit()
    return transaction_schema.dump(found_transaction)
  else:
    return 404


def update_account(account_body):
  found_transaction = db.session.query(
      Transaction).get(account_body['transaction_id'])
  if found_transaction:
    found_transaction.account_id = account_body['account_id']
    db.session.commit()
    return transaction_schema.dump(found_transaction)
  else:
    return 404


def update_amount(amount_body):
  found_transaction = db.session.query(
      Transaction).get(amount_body['transaction_id'])
  if found_transaction:
    found_transaction.amount = amount_body['amount']
    db.session.commit()
    return transaction_schema.dump(found_transaction)
  else:
    return 404


def update_description(description_body):
  found_transaction = db.session.query(
      Transaction).get(description_body['transaction_id'])
  if found_transaction:
    found_transaction.description = description_body['date']
    db.session.commit()
    return transaction_schema.dump(found_transaction)
  else:
    return 404
    

def delete_transaction(transaction_id):
    db.session.query(Transaction).filter_by(id=transaction_id).delete()
    db.session.commit()


# Configuration

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

from models import Transaction, TransactionSchema


transaction_schema = TransactionSchema()


if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
