FROM python:3.9-slim
LABEL authors="ogahserge"

WORKDIR /epidemietrackr-app

# venv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip

# --- Dépendances système minimales (compatibles Debian trixie) ---
# NB: pas de software-properties-common / gnupg2 / dirmngr / lsb-release
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    postgresql-client \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Variables GDAL (souvent suffisant sans fixer un .so spécifique)
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_DATA=/usr/share/gdal

# Si tu tiens à définir la lib GDAL explicitement, dé-commente :
# RUN ln -s /usr/lib/x86_64-linux-gnu/libgdal.so /usr/lib/libgdal.so || true
# ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

# Dépendances Python
COPY requirements.txt /epidemietrackr-app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . /epidemietrackr-app/

EXPOSE 8000
CMD ["gunicorn", "epidemietrackr.wsgi:application", "--bind=0.0.0.0:8000", "--workers=4", "--timeout=180", "--log-level=debug"]

#FROM python:3.9-slim
#LABEL authors="ogahserge"
#
#WORKDIR /epidemietrackr-app
#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#
## Upgrade pip
#RUN pip install --upgrade pip
#
## Install system dependencies including g++ and GDAL
#RUN apt-get update && \
#    apt-get install -y --no-install-recommends \
#    g++ \
#    gcc \
#    gdal-bin \
#    libgdal-dev \
#    libpq-dev \
#    software-properties-common \
#    ca-certificates \
#    dirmngr \
#    gnupg2 \
#    lsb-release \
#    postgresql-client && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*
#
## Set GDAL environment variables
#ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
#ENV C_INCLUDE_PATH=/usr/include/gdal
#ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
#
## Copy the requirements.txt and install Python dependencies
#COPY requirements.txt /epidemietrackr-app/requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
#
## Copy the rest of the application
#COPY . /epidemietrackr-app/
#
## Expose port 8000
#EXPOSE 8000
#
## Start the application using Gunicorn
#CMD ["gunicorn", "epidemietrackr.wsgi:application", "--bind=0.0.0.0:8000", "--workers=4", "--timeout=180", "--log-level=debug"]
