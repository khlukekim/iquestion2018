sudo uwsgi --http :80 --wsgi-file main.py --callable app --processes 8 --threads 16 --virtualenv $VIRTUAL_ENV
