release: python manage.py migrate && python manage.py create_subjects
web: gunicorn --config gunicorn.conf.py --bind 0.0.0.0:$PORT abitur_test.wsgi:application
