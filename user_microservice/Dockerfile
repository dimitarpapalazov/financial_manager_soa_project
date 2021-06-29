FROM python:3.6

COPY ./migrations /user_microservice/migrations
COPY *.py /user_microservice/
COPY *.yml /user_microservice/
COPY app.db /user_microservice/app.db
COPY ./requirements.txt /user_microservice/requirements.txt

WORKDIR /user_microservice

RUN pip install -r requirements.txt
EXPOSE 5006


CMD python app.py