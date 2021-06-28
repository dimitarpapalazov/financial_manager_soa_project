import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
import pathlib
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

def categories(user_id):
    categories = urllib.request.urlopen(
        'http://192.168.0.108:5003/api/settings/get-all-categories-by-user/' + str(user_id)).read().decode('utf-8')
    return categories
    categories = json.loads(categories)


def accounts(user_id):
    accounts = urllib.request.urlopen(
        'http://192.168.0.108:5001/api/accounts/get-all-by-user/' + str(user_id)).read().decode('utf-8')
    return accounts
    accounts = json.loads(accounts)


def transactions(user_id):
    transactions = urllib.request.urlopen(
        'http://192.168.0.108:5005/api/transactions/get-all-by-user/' + str(user_id)).read().decode('utf-8')
    return transactions
    transactions = json.loads(transactions)


def all(user_id):
    f = open('backup.json', 'w')
    f.write('{\n'+
    '"data": [\n'
    '{\n'+
    '"name": "Categories",\n' +
    '"data": ')
    f.write(str(categories(user_id)))
    f.write('},\n')
    f.write('{\n'+
    '"name": "Accounts",\n' +
    '"data": ')
    f.write(str(accounts(user_id)))
    f.write('},\n')
    f.write('{\n' +
            '"name": "Transactions",\n' +
            '"data": ')
    f.write(str(transactions(user_id)))
    f.write('}]\n')
    f.write('}\n')
    return {'backup': str(pathlib.Path('backup.json').absolute())}


# Configuration

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")


if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5002, debug=True)
