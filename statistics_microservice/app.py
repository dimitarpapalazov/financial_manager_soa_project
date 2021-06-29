from ast import parse
import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
import matplotlib.pyplot as plt
import pathlib
import json
import urllib
import requests
from consul import Consul, Check
import configparser
import netifaces
import socket


CONSUL_PORT = 8500
SERVICE_NAME = 'statistics_microservice'
SERVICE_PORT = 5004


def get_host_name_IP():

    host_name_ip = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_name_ip = s.getsockname()[0]
        s.close()
        # print ("Host ip:", host_name_ip)
        return host_name_ip
    except:
        print("Unable to get Hostname")


def register_to_consul():
    consul = Consul(host="consul", port=CONSUL_PORT)

    agent = consul.agent

    service = agent.service

    ip = get_host_name_IP()
    print(ip, SERVICE_PORT)

    check = Check.http(f"http://{ip}:{SERVICE_PORT}/api/statistics/ui",
                       interval="10s", timeout="5s", deregister="1s")

    service.register(name=SERVICE_NAME, service_id=SERVICE_NAME,
                     address=ip, port=SERVICE_PORT, check=check)


def get_consul_service(service_id):
    consul = Consul(host="consul", port=CONSUL_PORT)

    agent = consul.agent

    service_list = agent.services()

    service_info = service_list[service_id]

    return service_info['Address'], service_info['Port']


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


def get_body(user_id, date, type):
    return {'user_id': user_id,
            'date': date,
            'type': type}


def period_body(user_id, start, end, type):
    return {'user_id': user_id,
            'start': start,
            'end': end,
            'type': type}


def sort_data_by_categories(data):
    categories = []
    for i in data:
        print(i['category_id'])
        if i['category_id'] not in categories:
            categories.append(i['category_id'])
    print(len(categories))
    transactions_by_category = [0] * len(categories)
    for i in range(len(categories)):
        for t in data:
            if t['category_id'] == categories[i]:
                transactions_by_category[i] += t['amount']
    return categories, transactions_by_category


def create_plot(data):
    categories, transactions = sort_data_by_categories(data)
    fig, ax = plt.subplots()
    print(categories, transactions)
    ax.pie(transactions, labels=categories)
    ax.axis('equal')
    plt.savefig('pie_chart.png', dpi=300, bbox_inches='tight')
    return {'pie_chart': str(pathlib.Path('pie_chart.png').absolute())}

# Endpoints


def income_daily(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-daily', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def income_weekly(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-weekly', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def income_monthly(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-monthly', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def income_annually(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-annually', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def income_period(period_body):
    data = json.dumps(period_body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-period', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def expense_daily(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-daily', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def expense_weekly(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-weekly', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def expense_monthly(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-monthly', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def expense_annually(body):
    data = json.dumps(body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-annually', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


def expense_period(period_body):
    data = json.dumps(period_body)
    r = requests.post(
        'http://192.168.0.108:5005/api/transactions/get-period', data=data, headers={'Content-Type': 'application/json'}).json()
    return create_plot(r)


# Configuration


connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

register_to_consul()



if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5004, debug=True)
