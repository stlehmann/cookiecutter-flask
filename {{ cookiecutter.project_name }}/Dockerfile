FROM python:alpine
RUN apk update && apk add nginx
RUN mkdir -p /run/nginx
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./requirements.txt /flask-app/requirements.txt
WORKDIR /flask-app
RUN pip3 install gunicorn -r requirements.txt
COPY ./config.py ./wsgi.py /flask-app/
COPY ./app/ /flask-app/app
EXPOSE 5000
CMD nginx && gunicorn wsgi:application -b0.0.0.0:5000
