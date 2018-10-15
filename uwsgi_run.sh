sudo uwsgi --http :80 --wsgi-file main.py --callable app --processes 8 --threads 16 --daemonize uwsgi.log --virtualenv $VIRTUAL_ENV
