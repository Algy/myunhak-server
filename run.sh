uwsgi --http :80 --wsgi-file application.wsgi --master --processes 4 --threads 5  --venv ./venv
