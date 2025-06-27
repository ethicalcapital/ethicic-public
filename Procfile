release: ./build.sh
web: ./runtime_init.sh gunicorn ethicic.wsgi --bind 0.0.0.0:$PORT --log-file - --log-level info --access-logfile - --error-logfile -