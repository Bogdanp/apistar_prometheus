import time

from apistar import Component, Route, http
from prometheus_client import Counter, Gauge, Histogram

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
    def track_request_start(self, method, handler=None):
        self.start_time = time.monotonic()

        handler_name = "<builtin>"
        if handler is not None:
            handler_name = "%s.%s" % (handler.__module__, handler.__name__)

        REQUESTS_INPROGRESS.labels(method, handler_name).inc()

    def track_request_end(self, method, handler, response):
        handler_name = "<builtin>"
        if handler is not None:
            handler_name = "%s.%s" % (handler.__module__, handler.__name__)

        duration = time.monotonic() - self.start_time
        REQUEST_DURATION.labels(method, handler_name).observe(duration)
        REQUEST_COUNT.labels(method, handler_name, response.status_code).inc()
        REQUESTS_INPROGRESS.labels(method, handler_name).dec()


class PrometheusComponent(Component):
    def resolve(self) -> Prometheus:
        return Prometheus()


class PrometheusHooks:
    def on_request(self, prometheus: Prometheus, method: http.Method, route: Route) -> None:
        prometheus.track_request_start(method, route and route.handler)

    def on_response(self, prometheus: Prometheus, method: http.Method, route: Route, response: http.Response) -> http.Response:  # noqa
        prometheus.track_request_end(method, route and route.handler, response)
        return response

    def on_error(self, prometheus: Prometheus, method: http.Method, response: http.Response) -> http.Response:
        prometheus.track_request_start(method)
        prometheus.track_request_end(method, None, response)
        return response
