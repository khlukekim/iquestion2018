sudo nohup ./bin/gunicorn --worker-class eventlet -w 1 --bind=0.0.0.0:80 main:app &

