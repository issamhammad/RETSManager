FROM python:3.5.4-onbuild
ENV PYTHONUNBUFFERED 1

RUN mkdir /config
ADD requirements.txt /config/
RUN pip install -r /config/requirements.txt

