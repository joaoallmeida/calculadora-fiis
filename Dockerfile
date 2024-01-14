FROM python:3.10.12-slim

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
                        libatlas-base-dev \
                        python3-dev \
                        build-essential \ 
                        libssl-dev \
                        libffi-dev

WORKDIR /app
COPY /app /app
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt 

EXPOSE 5000
CMD ["uwsgi", "--ini", "./wsgi.ini"]