FROM python:3.9-slim-buster

EXPOSE 5000

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-pymysql \
    bash \
    bash-completion \
    vim


COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /var/www/src
RUN mkdir -p /export/certs
RUN mkdir -p /log
COPY src/ /var/www/src

WORKDIR /var/www

COPY setup.py setup.py
RUN pip install -e ./

COPY tests/ tests/
COPY config/ config/
COPY bin/ bin/
CMD chmod a+x bin/run_workers.py
CMD chmod a+x bin/console.py

WORKDIR /var/www/src

CMD flask run --host=0.0.0.0 --port=5000
