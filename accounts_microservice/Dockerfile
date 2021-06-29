FROM python:3.6

COPY ./migrations /accounts_microservice/migrations
COPY *.py /accounts_microservice/
COPY *.yml /accounts_microservice/
COPY app.db /accounts_microservice/app.db
COPY ./requirements.txt /accounts_microservice/requirements.txt

WORKDIR /accounts_microservice

RUN pip install -r requirements.txt
EXPOSE 5001


CMD python app.py