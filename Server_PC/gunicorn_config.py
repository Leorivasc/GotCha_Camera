# gunicorn_config.py
bind = "0.0.0.0:5000"
workers = 1
worker_class = "gevent"
timeout = 0
threaded = True
