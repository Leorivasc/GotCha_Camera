# gunicorn_config.py
bind = "0.0.0.0:8080"
workers = 8
worker_class = "gevent"
timeout = 0
threads = 50
