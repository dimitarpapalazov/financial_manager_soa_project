from transactions_microservice.models import Transaction
import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from user_microservice.models import User
from user_microservice.app import db as user_db
from settings_microservice.app import db as categories_db
from settings_microservice.models import Category
from accounts_microservice.models import Account
from accounts_microservice.app import db as accounts_db
from transactions_microservice.app import db as transactions_db
import pathlib


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

def categories_to_csv(user_id):
    found_user = user_db.session.query(User).get(user_id)
    if found_user:
        categories_csv = ''
        categories = categories_db.session.query(
            Category).filter_by(user_id=user_id).all()
        for category in categories:
            categories_csv += category.to_csv() + '\n'
        return categories_csv
    else:
        return 404


def accounts_to_csv(user_id):
    found_user = user_db.session.query(User).get(user_id)
    if found_user:
        accounts_csv = ''
        accounts = accounts_db.session.query(
            Account).filter_by(user_id=user_id).all()
        for account in accounts:
            accounts_csv += account.to_csv() + '\n'
        return accounts_csv
    else:
        return 404


def transactions_to_csv(user_id):
    found_user = user_db.session.query(User).get(user_id)
    if found_user:
        transactions_csv = ''
        transactions = transactions_db.session.query(
            Transaction).filter_by(user_id=user_id).all()
        for transaction in transactions:
            transactions_csv += transaction.to_csv() + '\n'
        return transactions_csv
    else:
        return 404


def all_to_csv(user_id):
    f = open('backup.csv', 'w')
    f.write('Categories:\n')
    f.write(categories_to_csv(user_id))
    f.write('Accounts:\n')
    f.write(accounts_to_csv(user_id))
    f.write('Transactions:\n')
    f.write(transactions_to_csv(user_id))
    return {'backup': pathlib.Path(f).absolute()}


# Configuration

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")


if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5002, debug=True)
