from apistar import http
from apistar.types import Handler, ReturnValue

from .components import Prometheus


def before_request(prometheus: Prometheus,
                   method: http.Method,
                   handler: Handler):
    prometheus.track_request_start(method, handler)


def after_request(prometheus: Prometheus,
                  method: http.Method,
                  handler: Handler,
                  ret: ReturnValue):
    prometheus.track_request_end(method, handler, ret)
    return ret
