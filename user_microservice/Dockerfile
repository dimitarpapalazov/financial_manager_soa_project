FROM python:3.6

WORKDIR /user_microservice

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "/user_microservice/app.py"]
