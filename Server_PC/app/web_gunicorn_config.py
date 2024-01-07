# gunicorn_config.py
bind = "0.0.0.0:8080"
workers = 4
#worker_class = "gevent"
timeout = 0
threaded = False
