FROM python:latest
RUN apt -y update && apt -y upgrade && \
    apt -y install redis-server supervisor && \
    mkdir /code
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt
COPY . /code
COPY supervisord.conf /etc/supervisor/conf.d/celery.conf
WORKDIR /code
RUN chmod a+x *.sh
RUN python manage.py migrate && python manage.py migrate --run-syncdb
RUN python manage.py loaddata fixtures.json
CMD ["service redis-server start", "service supervisor start" ]