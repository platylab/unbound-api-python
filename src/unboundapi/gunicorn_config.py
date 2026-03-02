import os


workers = int(os.environ.get("UNBOUNDAPI_PROCESSES", "2"))
threads = int(os.environ.get("UNBOUNDAPI_THREADS", "4"))
bind = os.environ.get("UNBOUNDAPI_BIND", "127.0.0.1:8080")


forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}

# Logging
accesslog = os.environ.get("UNBOUNDAPI_ACCESSLOG", "-")
errorlog = os.environ.get("UNBOUNDAPI_ERRORLOG", "-")

# Custom access log format
access_log_format = '%({x-forwarded-for}i)s %(l.md)s %(u.md)s %(t.md)s "%(r.md)s" %(s.md)s %(b.md)s "%(f.md)s" "%(a.md)s"'
