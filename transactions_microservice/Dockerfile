FROM python:3.6

COPY ./migrations /transactions_microservice/migrations
COPY *.py /transactions_microservice/
COPY *.yml /transactions_microservice/
COPY app.db /transactions_microservice/app.db
COPY ./requirements.txt /transactions_microservice/requirements.txt

WORKDIR /transactions_microservice

RUN pip install -r requirements.txt
EXPOSE 5005


CMD python app.py