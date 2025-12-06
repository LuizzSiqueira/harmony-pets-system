# Gunicorn configuration file
import multiprocessing
import os

# Binding
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Workers
workers = int(os.environ.get('GUNICORN_WORKERS', '2'))
worker_class = 'sync'
worker_connections = 1000
threads = int(os.environ.get('GUNICORN_THREADS', '2'))

# Timeouts
timeout = 120  # 2 minutos (para operações de login/2FA)
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'harmony-pets'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (deixar None, Render gerencia)
keyfile = None
certfile = None

# Preload
preload_app = False  # Não preload para economizar memória

# Worker restart
max_requests = 1000  # Reinicia worker após 1000 requests
max_requests_jitter = 50  # Jitter para evitar restart simultâneo
