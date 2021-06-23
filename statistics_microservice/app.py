import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from transactions_microservice.app import get_daily, get_weekly, get_monthly, get_annually, get_period
import matplotlib.pyplot as plt
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


def get_body(user_id, date, type, to_JSON):
    return {'user_id': user_id,
            'date': date,
            'type': type,
            'to_JSON': to_JSON}


def period_body(user_id, start, end, type, to_JSON):
    return {'user_id': user_id,
            'start': start,
            'end': end,
            'type': type,
            'to_JSON': to_JSON}


def sort_data_by_categories(data):
    categories = (i.category_id for i in data)
    transactions_by_category = [0] * len(categories)
    for i in range(len(categories)):
        for t in data:
            if t.category_id == categories[i]:
                transactions_by_category[i] += t.amount
    return categories, transactions_by_category


def create_plot(data):
    categories, transactions = sort_data_by_categories(data)
    fig, ax = plt.subplots()
    ax.pie(transactions, labels=categories)
    ax.axis('equal')
    plt.savefig('pie_chart.png', dpi=300, bbox_inches='tight')
    return {'pie_chart': pathlib.Path('pie_chart.png').absolute()}

# Endpoints


def income_daily(body):
    data = get_daily(get_body(body['user_id'], body['date'], 1, False))
    return create_plot(data)


def income_weekly(body):
    data = get_weekly(get_body(body['user_id'], body['date'], 1, False))
    return create_plot(data)


def income_monthly(body):
    data = get_monthly(get_body(body['user_id'], body['date'], 1, False))
    return create_plot(data)


def income_annually(body):
    data = get_annually(get_body(body['user_id'], body['date'], 1, False))
    return create_plot(data)


def income_period(period_body):
    data = get_annually(
        get_body(period_body['user_id'], period_body['start'], period_body['end'], 1, False))
    return create_plot(data)


def expense_daily(body):
    data = get_daily(get_body(body['user_id'], body['date'], 0, False))
    return create_plot(data)


def expense_weekly(body):
    data = get_weekly(get_body(body['user_id'], body['date'], 0, False))
    return create_plot(data)


def expense_monthly(body):
    data = get_monthly(get_body(body['user_id'], body['date'], 0, False))
    return create_plot(data)


def expense_annually(body):
    data = get_annually(get_body(body['user_id'], body['date'], 0, False))
    return create_plot(data)


def expense_period(period_body):
    data = get_annually(
        get_body(period_body['user_id'], period_body['start'], period_body['end'], 0, False))
    return create_plot(data)


# Configuration


connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")


if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5000, debug=True)
