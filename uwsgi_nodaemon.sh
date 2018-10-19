sudo ./bin/uwsgi --http :80 --wsgi-file main.py --callable app --gevent 1000 --http-websockets --master --virtualenv $VIRTUAL_ENV
