FROM python:3.10-alpine

ENV HOST 0.0.0.0
ENV PORT 8000

COPY . /api
WORKDIR /api

RUN apk add build-base

RUN pip install -r requirements.txt

EXPOSE 8000

RUN pip install gunicorn

CMD ["flask","db","init"]

CMD ["flask","db","migrate"]

CMD ["flask","db","upgrade"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3","--timeout", "6000", "app:app"]