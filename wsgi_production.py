#!/usr/bin/env python
"""WSGI config for production deployment."""

import os
from django.core.wsgi import get_wsgi_application

# Production sozlamalarini ishlatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abitur_test.production_settings')

application = get_wsgi_application()