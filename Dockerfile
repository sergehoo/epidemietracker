#FROM python:3.9-slim
#LABEL authors="ogahserge"
#
#ENV DJANGO_SETTINGS_MODULE=epidemietrackr.settings
#
#WORKDIR /epidemietrackr-app
#
#COPY requirements.txt /epidemietrackr-app/requirements.txt
#
## Installer les dépendances système nécessaires pour GDAL et PostgreSQL
#RUN apt-get update && \
#    apt-get install -y --no-install-recommends \
#    gdal-bin \
#    libgdal-dev \
#    libpq-dev \
#    gcc \
#    && apt-get clean && \
#    rm -rf /var/lib/apt/lists/*
#
## Définir la variable d'environnement pour GDAL
#ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
#ENV C_INCLUDE_PATH=/usr/include/gdal
#ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
## Installer les dépendances Python
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . /epidemietrackr-app/
#
## Exposer le port sur lequel l'application Django sera accessible
#EXPOSE 8000
#RUN python3 manage.py migrate
## Démarrer l'application
#CMD ["./wait-for-it.sh", "epidemietrackrDB:5432", "--","gunicorn", "epidemietrackr.wsgi:application", "--bind=0.0.0.0:8000"]
#
#
#ENV DJANGO_SETTINGS_MODULE=epidemietrackr.settings


FROM python:3.9-slim
LABEL authors="ogahserge"

#ENV DJANGO_SETTINGS_MODULE=epidemietrackr.settings

WORKDIR /epidemietrackr-app
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY requirements.txt /epidemietrackr-app/requirements.txt

# Install the required packages before adding repositories
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    dirmngr \
    gnupg2 \
    lsb-release \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add the ubuntugis-unstable repository and install GDAL
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin=3.9.2+dfsg-1~focal0 \
    libgdal-dev=3.9.2+dfsg-1~focal0 \
    libpq-dev \
    gcc \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Définir la variable d'environnement pour GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

COPY . /epidemietrackr-app/

RUN apt-get update && apt-get install -y postgresql-client
# Exposer le port sur lequel l'application Django sera accessible
EXPOSE 8000

# Démarrer l'application
#CMD ["gunicorn", "epidemietrackr.wsgi:application", "--bind=0.0.0.0:8000"]
CMD ["gunicorn", "epidemietrackr.wsgi:application", "--bind=0.0.0.0:8000", "--workers=4", "--timeout=180", "--log-level=debug"]
#CMD ["gunicorn", "epidemietrackr.wsgi:application", "--bind=0.0.0.0:8000", "--timeout=180", "--log-level=debug"]