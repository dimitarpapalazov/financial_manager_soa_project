FROM python:3.6

COPY *.py /backup_microservice/
COPY *.yml /backup_microservice/
COPY ./requirements.txt /backup_microservice/requirements.txt

WORKDIR /backup_microservice

RUN pip install -r requirements.txt
EXPOSE 5002


CMD python app.py