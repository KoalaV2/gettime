FROM python:3.8-alpine as flaskapp
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN apk add gcc
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD ["main.py" ]

FROM python:3.8-alpine as discordbot
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN apk add gcc
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD ["discordBot.py" ]
