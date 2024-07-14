FROM python:3.12-slim

ENV FLSK_SECRET_KEY="sd?fadf43#5q4ghb!x"
WORKDIR /proj
COPY requirements.txt requirements.txt
COPY ./app /proj/app/

RUN pip install -r requirements.txt
RUN python -m app.initdb
EXPOSE 5000
CMD gunicorn --bind 0.0.0.0:5000 app.wsgi:app