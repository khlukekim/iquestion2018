sudo uwsgi --http :80 --wsgi-file main.py --callable app --processes 4 --threads 16 --daemonize uwsgi.log
