FROM python:stretch
COPY requirements.txt owl-post/ /usr/src/app/ 
WORKDIR /usr/src/app
RUN mkdir qdisambiguation_files
RUN apt-get update && apt-get -y upgrade
RUN pip install --no-cache-dir -r requirements.txt
CMD python hermes.py -r config.yaml


