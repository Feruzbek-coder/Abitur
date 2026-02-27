# Gunicorn configuration file
bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
tmp_upload_dir = None
errorlog = "-"
accesslog = "-"
loglevel = "info"