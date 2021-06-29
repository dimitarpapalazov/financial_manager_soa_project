from models import User, UserSchema
from functools import wraps
import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from random import randint
from flask_mail import Mail, Message
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import secrets
import string
import jwt
import time


# Authentication and authorization configuration

JWT_SECRET = 'USER MS SECRET'
JWT_LIFETIME_SECONDS = 600000

ACCOUNTS_APIKEY = "ACCOUNTS MS SECRET"
BACKUP_APIKEY = "BACKUP MS SECRET"
SETTINGS_APIKEY = "SETTINGS MS SECRET"
STATISTICS_APIKEY = "STATISTICS MS SECRET"
TRANSACTIONS_APIKEY = "TRANSACTIONS MS SECRET"


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

def auth(auth_body):
    timestamp = int(time.time())
    found_user = db.session.query(User).filter_by(
        username=auth_body['username']).first()
    user_id = found_user.id
    roles = []
    roles.append(found_user.role)
    payload = {
        "iss": 'User Microservice',
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": user_id,
        "roles": roles,
        "user-details": user_schema.dump(found_user)
    }
    encoded = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return encoded


def auth_microservice(auth_body_microservice):
    apikey = auth_body_microservice['apikey']
    roles = []
    if apikey == ACCOUNTS_APIKEY:
        roles.append("ACCOUNTS")
        sub = 'ACCOUNTS'
    elif apikey == BACKUP_APIKEY:
        roles.append("BACKUP")
        sub = 'BACKUP'
    elif apikey == SETTINGS_APIKEY:
        roles.append("SETTINGS")
        sub = 'SETTINGS'
    elif apikey == STATISTICS_APIKEY:
        roles.append("STATISTICS")
        sub = 'STATISTICS'
    elif apikey == TRANSACTIONS_APIKEY:
        roles.append("TRANSACTIONS")
        sub = 'TRANSACTIONS'

    timestamp = int(time.time())
    payload = {
        "iss": 'Financial Manager',
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": sub,
        "roles": roles
    }
    encoded = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return encoded


def send_verification_email(user_id):
    found_user = db.session.query(User).get(user_id)
    if found_user:
        msg = Message('Hello', sender='soauserms@gmail.com',
                      recipients=[found_user.email])
        msg.subject = 'Verification Code For Your Account'
        msg.body = "Dear "+str(found_user.name)+" "+str(found_user.surname) + \
            ",\n" + "Your verificaiton code is: " + \
            str(found_user.verification_code)
        mail.send(msg)
        return 200
    else:
        return 404


def registration(user_body):
    found_user = db.session.query(User).filter_by(
        username=user_body['username']).first()
    if not found_user:
        if user_body['password'] == user_body['repeated_password']:
            date_of_birth = datetime.strptime(
                user_body['date_of_birth'], '%m-%d-%Y')
            today = date.today()
            age = relativedelta(today, date_of_birth).years
            letter_and_digits = string.ascii_letters + string.digits
            code = ''.join(secrets.choice(letter_and_digits) for i in range(6))
            new_user = User(username=user_body['username'],
                            email=user_body['email'],
                            name=user_body['name'],
                            surname=user_body['surname'],
                            password=bcrypt.generate_password_hash(
                                user_body['password']),
                            role='BASIC',
                            is_verified=False,
                            date_of_birth=date_of_birth,
                            gender=user_body['gender'],
                            age=age,
                            verification_code=code)
        else:
            return 400
    else:
        return 409
    db.session.add(new_user)
    db.session.commit()
    send_verification_email(new_user.id)
    return user_schema.dump(new_user)


def get_role(user_id):
    found_user = db.session.query(User).get(user_id)
    if found_user:
        return {'role': found_user.role}
    else:
        return 404


def get_user_details(user_id):
    found_user = db.session.query(User).get(user_id)
    if found_user:
        return user_schema.dump(found_user)
    else:
        return 404


@has_role(['ADMIN', 'BASIC'])
def change_password(password_body):
    found_user = db.session.query(User).get(password_body['user_id'])
    if found_user:
        if bcrypt.check_password_hash(found_user.password, password_body['old_password']):
            found_user.password = bcrypt.generate_password_hash(
                password_body['new_password'])
            db.session.commit()
            return user_schema.dump(found_user)
        else:
            return 400
    else:
        return 404


@has_role(["ADMIN", "BASIC"])
def verify_user(verification_body):
    found_user = db.session.query(User).get(verification_body['user_id'])
    if found_user:
        if found_user.verification_code == verification_body['code']:
            found_user.is_verified = True
            db.session.commit()
            return 200
        else:
            return 400
    else:
        return 404


def get_all_users():
    users = db.session.query(User).all()
    return user_schema.dump(users, many=True)


@has_role(["ADMIN"])
def delete_user(user_id):
    db.session.query(User).filter_by(id=user_id).delete()
    db.session.commit()


# Configuration

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

# TODO: May need change
# Setup for mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'soauserms@gmail.com'
app.config['MAIL_PASSWORD'] = 'soauserms123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


user_schema = UserSchema(
    exclude=['is_verified', 'password', 'verification_code'])


if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5006, debug=True)
