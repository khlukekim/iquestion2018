sudo ./bin/uwsgi --http :80 --wsgi-file main.py --callable app --daemonize uwsgi.log --virtualenv $VIRTUAL_ENV --gevent 100 --http-websockets --master --threads 16
