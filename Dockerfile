FROM python:3.9-slim
LABEL authors="ogahserge"

ENV DJANGO_SETTINGS_MODULE=epidemietrackr.settings

WORKDIR /epidemietrackr-app

COPY requirements.txt /epidemietrackr-app/requirements.txt

RUN pip install -r requirements.txt
RUN apt-get update && \
    apt-get install -y \
    gdal-bin \
    libgdal-dev

COPY . /epidemietrackr-app/

#RUN python3 manage.py makemigrations && python3 manage.py migrate

CMD ["gunicorn","epidemietrackr.wsgi:application","--bind=0.0.0.0:8000"]