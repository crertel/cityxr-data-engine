#FROM python:3.8 as base
#FROM base as builder

FROM python:3.8-slim

RUN apt-get update \
    && apt-get install unixodbc -y \
    && apt-get install unixodbc-dev -y \
    && apt-get install freetds-dev -y \
    && apt-get install freetds-bin -y \
    && apt-get install tdsodbc -y \
    && apt-get install --reinstall build-essential -y

# populate "ocbcinst.ini"
RUN echo "[FreeTDS]\n\
    Description = FreeTDS unixODBC Driver\n\
    Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
    Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini


COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY . /app
COPY docker-entry.sh /app/docker-entry.sh
WORKDIR /app
CMD ["./docker-entry.sh"]