# Gunicorn configuration for production

# Server socket
bind = "127.0.0.1:8001"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "/var/log/myweb/access.log"
errorlog = "/var/log/myweb/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "myweb"

# Daemon mode
daemon = False
# pidfile = "/var/run/myweb/myweb.pid"  # Disabled - systemd manages the process

# User/group to run as
# user = "www-data"
# group = "www-data"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (будет настроено позже)
# keyfile = "/etc/ssl/private/mshkdev.ru.key"
# certfile = "/etc/ssl/certs/mshkdev.ru.crt"