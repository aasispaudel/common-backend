FROM python:3.12.3-bookworm
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && pip install -r /code/requirements.txt
RUN apt-get -y update && apt-get -y upgrade
COPY ./app /code/app
EXPOSE 8000
