FROM python:3.10.12

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
                        libatlas-base-dev \
                        python3-dev

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt 

EXPOSE 5000
CMD ["uwsgi", "--ini", "./wsgi.ini"]