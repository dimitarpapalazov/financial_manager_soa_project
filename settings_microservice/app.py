import connexion
from flask import request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import jwt
from consul import Consul, Check
import configparser
import netifaces
import socket


CONSUL_PORT = 8500
SERVICE_NAME = 'settings_microservice'
SERVICE_PORT = 5003


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

    check = Check.http(f"http://{ip}:{SERVICE_PORT}/api/settings/ui",
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


# Endpoints

def create_currency(currency_body):
  found_currency = db.session.query(Currency).filter_by(
      name=currency_body['name']).first()
  if not found_currency:
    new_currency = Currency(name=currency_body['name'],
                            short_name=currency_body['short_name'],
                            value_to_eur=currency_body['value_to_eur'])
    db.session.add(new_currency)
    db.session.commit()
    return currency_schema.dump(new_currency)
  else:
    return 409

    
def get_currency(currency_id):
  found_currency = db.session.query(Currency).get(currency_id)
  if found_currency:
    return currency_schema.dump(found_currency)
  else:
    return 404


def get_all_currencies():
  currencies = db.session.query(Currency).all()
  return currency_schema.dump(currencies, many=True)


def update_currency_value(value_body):
  found_currency = db.session.query(Currency).get(value_body['currency_id'])
  if found_currency:
    found_currency.value_to_eur = value_body['value']
    db.session.commit()
    return currency_schema.dump(found_currency)
  else:
    return 404


def delete_currency(currency_id):
    db.session.query(Currency).filter_by(id=currency_id).delete()
    db.session.commit()


def exchange_currency(first_currency_id, second_currency_id, user_id):
  pass


def create_category(category_body):
    found_category = db.session.query(Category).filter_by(
        name=category_body['name'], user_id=category_body['user_id']).first()
    if not found_category:
      new_category = Category(name=category_body['name'],
                              type=category_body['type'],
                              user_id=category_body['user_id'])
      db.session.add(new_category)
      db.session.commit()
      return category_schema.dump(new_category)
    else:
      return 409


def get_category(category_id):
  found_category = db.session.query(Category).get(category_id)
  if found_category:
    return category_schema.dump(found_category)
  else:
    return 404


def get_all_categories_by_user_id(user_id):
    categories = db.session.query(Category).filter_by(user_id=user_id).all()
    return category_schema.dump(categories, many=True)


def update_category_name(name_body):
  found_category = db.session.query(Category).get(name_body['category_id'])
  if found_category:
    found_category.name = name_body['name']
    db.session.commit()
    return category_schema.dump(found_category)
  else:
    return 404


def delete_category(category_id):
    db.session.query(Category).filter_by(id=category_id).delete()
    db.session.commit()

# Configuration

connexion_app = connexion.App(__name__, specification_dir="./")
app = connexion_app.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
connexion_app.add_api("api.yml")

register_to_consul()


from models import Category, Currency, CategorySchema, CurrencySchema


category_schema = CategorySchema()
currency_schema = CurrencySchema()


if __name__ == "__main__":
    connexion_app.run(host='0.0.0.0', port=5003, debug=True)
