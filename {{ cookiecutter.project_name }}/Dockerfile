FROM python:3.7.3-stretch
RUN apt-get update && apt-get install -y nginx cron
RUN mkdir -p /run/nginx
COPY ./requirements.txt /flaskapp/requirements.txt
COPY ./nginx/flaskapp /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled/flaskapp
WORKDIR /flaskapp
RUN pip3 install -r requirements.txt
COPY ./backup.py /flaskapp/backup.py
COPY ./backup.sh /etc/cron.daily/backup.sh
COPY ./wsgi.py /flaskapp/
COPY ./app/ /flaskapp/app
EXPOSE 5000 8000
CMD nginx && gunicorn wsgi:application -b0.0.0.0:5000
