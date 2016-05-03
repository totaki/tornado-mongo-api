FROM python:3.5
RUN mkdir /app
COPY requirements.txt /var/tmp/requirements.txt
RUN pip install -r /var/tmp/requirements.txt
WORKDIR /app
