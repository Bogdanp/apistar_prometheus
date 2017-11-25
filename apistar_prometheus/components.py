import time

from apistar import http
from http import HTTPStatus
from prometheus_client import Counter, Gauge, Histogram
from threading import local

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Time spent processing a request.",
    ["method", "handler"],
)
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Request count by method, handler and response code.",
    ["method", "handler", "code"],
)
REQUESTS_INPROGRESS = Gauge(
    "http_requests_inprogress",
    "Requests in progress by method and handler",
    ["method", "handler"],
)


class Prometheus:
    def __init__(self):
        self.data = local()

    def track_request_start(self, method, handler):
        self.data.start_time = time.monotonic()

        handler_name = "%s.%s" % (handler.__module__, handler.__name__)
        REQUESTS_INPROGRESS.labels(method, handler_name).inc()

    def track_request_end(self, method, handler, ret):
        status = 200
        if isinstance(ret, http.Response):
            status = HTTPStatus(ret.status).value

        handler_name = "<builtin>"
        if handler is not None:
            handler_name = "%s.%s" % (handler.__module__, handler.__name__)
            duration = time.monotonic() - self.data.start_time
            del self.data.start_time
            REQUEST_DURATION.labels(method, handler_name).observe(duration)

        REQUEST_COUNT.labels(method, handler_name, status).inc()
        REQUESTS_INPROGRESS.labels(method, handler_name).dec()
