FROM python:3.10.12-slim

WORKDIR /project

COPY . /project

RUN pip install -r requirements.txt

CMD [ "python", "app/main.py" ]