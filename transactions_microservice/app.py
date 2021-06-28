import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import date, datetime, timedelta
from calendar import monthrange
import urllib
import json


# Authorization configuration

def has_role(arg):
    def has_role_inner(fn):
        @wraps(fn)
        def decode_view(*args, **kwargs):
            try:
                headers = request.headers
                if 'Authorization' in headers:
                    token = headers['Authorization']
                    decoded_token = decode_token(token)
                    if 'admin' in decoded_token:
                        return fn(*args, **kwargs)
                    for role in arg:
                        if role in decoded_token['roles']:
                            return fn(*args, **kwargs)
                    abort(404)
                return fn(*args, **kwargs)
            except Exception as e:
                abort(401)

        return decode_view

    return has_role_inner


def decode_token(token):
    token = token.strip('"')
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])


# Endpoints

def create(transaction_body):
    new_transaction = Transaction(date=date.today(),
                                  category_id=transaction_body['category_id'],
                                  account_id=transaction_body['account_id'],
                                  amount=transaction_body['amount'],
                                  description=transaction_body['description'],
                                  user_id=transaction_body['user_id'])
    db.session.add(new_transaction)
    db.session.commit()
    return transaction_schema.dump(new_transaction)


def get(tranasction_id):
    found_transaction = db.session.query(Transaction).get(tranasction_id)
    if found_transaction:
        return transaction_schema.dump(found_transaction)
    else:
        return 404


def transactions_by_category(get_body, transactions):
    categories = urllib.request.urlopen(
        'http://192.168.0.108:5003/api/settings/get-all-categories-by-user/' + str(get_body['user_id'])).read().decode('utf-8')
    categories = json.loads(categories)
    categories_ids = []
    for i in range(len(categories)):
      if categories[i]['type'] != get_body['type']:
        categories.pop(i)
        continue
      if categories[i]['id'] not in categories_ids:
        categories_ids.append(categories[i]['id'])
    for i in range(len(transactions)):
      if transactions[i].category_id not in categories_ids:
        transactions.pop(i)
    return transactions


def get_daily(get_body):
    transactions = db.session.query(Transaction).filter(
        Transaction.user_id == get_body['user_id'], Transaction.date == get_body['date']).all()
    if get_body['type'] != -1:
        transactions = transactions_by_category(get_body, transactions)
    return transaction_schema.dump(transactions, many=True)


def get_weekly(get_body):
    date_body = get_body['date']
    date_body = date.fromisoformat(date_body)
    start = date_body - timedelta(days=date_body.weekday())
    end = start + timedelta(days=6)
    transactions = db.session.query(Transaction).filter(
        Transaction.user_id == get_body['user_id'], Transaction.date >= start, Transaction.date <= end).all()
    if get_body['type'] != -1:
      transactions = transactions_by_category(get_body, transactions)
    return transaction_schema.dump(transactions, many=True)


def get_monthly(get_body):
    date_body = get_body['date']
    date_body = date.fromisoformat(date_body)
    start = date_body - timedelta(days=date_body.day - 1)
    month, days = monthrange(date_body.year, date_body.month)
    end = start + timedelta(days=days - 1)
    transactions = db.session.query(Transaction).filter(
        Transaction.user_id == get_body['user_id'], Transaction.date >= start, Transaction.date <= end).all()
    if get_body['type'] != -1:
      transactions = transactions_by_category(get_body, transactions)
    return transaction_schema.dump(transactions, many=True)


def get_annually(get_body):
    date_body = get_body['date']
    date_body = date.fromisoformat(date_body)
    day_of_year = date_body.timetuple().tm_yday
    start = date_body - timedelta(days=day_of_year - 1)
    month, days = monthrange(date_body.year, 2)
    end = start + timedelta(days=366) if days == 29 else start + timedelta(days=365)
    transactions = db.session.query(Transaction).filter(
        Transaction.user_id == get_body['user_id'], Transaction.date >= start, Transaction.date <= end).all()
    if get_body['type'] != -1:
      transactions = transactions_by_category(get_body, transactions)
    return transaction_schema.dump(transactions, many=True)


def get_period(period_body):
    transactions = db.session.query(Transaction).filter(
        Transaction.user_id == period_body['user_id'], Transaction.date >= period_body['start'], Transaction.date <= period_body['end']).all()
    if period_body['type'] != -1:
      transactions = transactions_by_category(period_body, transactions)
    return transaction_schema.dump(transactions, many=True)


def update_date(date_body):
    found_transaction = db.session.query(
        Transaction).get(date_body['tranasction_id'])
    if found_transaction:
        date_formatted = date.fromisoformat(date_body['date'])
        found_transaction.date = date_formatted
        db.session.commit()
        return transaction_schema.dump(found_transaction)
    else:
        return 404


def update_account(account_body):
    found_transaction = db.session.query(
        Transaction).get(account_body['tranasction_id'])
    if found_transaction:
        found_transaction.account_id = account_body['account_id']
        db.session.commit()
        return transaction_schema.dump(found_transaction)
    else:
        return 404


def update_amount(amount_body):
    found_transaction = db.session.query(
        Transaction).get(amount_body['tranasction_id'])
    if found_transaction:
        found_transaction.amount = amount_body['amount']
        db.session.commit()
        return transaction_schema.dump(found_transaction)
    else:
        return 404


def update_description(description_body):
    found_transaction = db.session.query(
        Transaction).get(description_body['tranasction_id'])
    if found_transaction:
        found_transaction.description = description_body['description']
        db.session.commit()
        return transaction_schema.dump(found_transaction)
    else:
        return 404


def delete_transaction(tranasction_id):
    db.session.query(Transaction).filter_by(
        id=tranasction_id).delete()
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
    connexion_app.run(host='0.0.0.0', port=5005, debug=True)
