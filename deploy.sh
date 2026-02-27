#!/bin/bash

# Production deployment script

echo "🚀 Abitur Test Production Deployment"

# 1. Virtual environment yaratish
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies o'rnatish
pip install -r requirements.txt

# 3. Database migration
python manage.py migrate --settings=abitur_test.production_settings

# 4. Static fayllarni yig'ish
python manage.py collectstatic --noinput --settings=abitur_test.production_settings

# 5. Superuser yaratish (ixtiyoriy)
# python manage.py createsuperuser --settings=abitur_test.production_settings

# 6. Gunicorn bilan serverni ishga tushirish
gunicorn --config gunicorn.conf.py abitur_test.wsgi_production:application

echo "✅ Deployment completed!"