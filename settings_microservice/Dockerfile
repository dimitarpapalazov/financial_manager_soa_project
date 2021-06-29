FROM python:3.6

COPY ./migrations /settings_microservice/migrations
COPY *.py /settings_microservice/
COPY *.yml /settings_microservice/
COPY app.db /settings_microservice/app.db
COPY ./requirements.txt /settings_microservice/requirements.txt

WORKDIR /settings_microservice

RUN pip install -r requirements.txt
EXPOSE 5003


CMD python app.py