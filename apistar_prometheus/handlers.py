from apistar.http import Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, multiprocess

#: Micro-optimization to avoid allocating a new dict on every metrics
#: request.  Response itself copies the headers its given so this
#: shouldn't be a problem.
_HEADERS = {"content-type": CONTENT_TYPE_LATEST}


def expose_metrics():
    return Response(generate_latest(), headers=_HEADERS)


def expose_metrics_multiprocess():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), headers=_HEADERS)
