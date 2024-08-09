FROM python:3-12-slim

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]