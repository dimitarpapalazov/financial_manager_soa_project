FROM python:3.6

COPY *.py /statistics_microservice/
COPY *.yml /statistics_microservice/
COPY ./requirements.txt /statistics_microservice/requirements.txt

WORKDIR /statistics_microservice

RUN pip install -r requirements.txt
EXPOSE 5004


CMD python app.py