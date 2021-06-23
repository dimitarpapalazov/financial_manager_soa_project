import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from ..user_microservice.models import User


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

def create(account_body):
  found_user = db.session.query(User).get(account_body['user_id'])
  if not found_user:
    found_account = db.session.query(Account).filter_by(name=account_body['name']).first()
    if not found_account:
      new_account = Account(group=account_body['group'],
        name=account_body['name'],
        amount=0.0,
        user_id=account_body['user_id'])
      db.session.add(new_account)
      db.session.commit()
      return account_schema.dump(new_account)
    else:
      return 409
  else:
    return 404

    
def get_account(account_id):
  found_account = db.session.query(Account).get(account_id)
  if found_account:
    return account_schema.dump(found_account)
  else:
    return 404


def get_all_accounts_by_user_id(user_id):
  found_user = db.session.query(User).get(user_id)
  if found_user:
    accounts = db.session.query(Account).filter_by(user_id=user_id).all()
    return account_schema.dump(accounts, many=True)
  else:
    return 404


def change_name(name_body):
  found_account = db.session.query(Account).get(name_body['account_id'])
  if found_account:
    found_account.name = name_body['name']
    db.session.commit()
    return account_schema.dump(found_account)
  else:
    return 404


def change_group(group_body):
  found_account = db.session.query(Account).get(group_body['account_id'])
  if found_account:
    found_account.group = group_body['group']
    db.session.commit()
    return account_schema.dump(found_account)
  else:
    return 404


def change_amount(amount_body):
  found_account = db.session.query(Account).get(amount_body['account_id'])
  if found_account:
    found_account.amount += amount_body['amount']
    db.session.commit()
    return account_schema.dump(found_account)
  else:
    return 404


def delete_account(account_id):
    db.session.query(Account).filter_by(id=account_id).delete()
    db.session.commit()


# Configuration

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

from models import Account, AccountSchema


account_schema = AccountSchema()


if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
