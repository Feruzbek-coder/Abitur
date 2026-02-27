release: python manage.py migrate && python manage.py create_subjects
web: gunicorn --config gunicorn.conf.py abitur_test.wsgi:application
