from apistar import Response, annotate, http
from apistar.renderers import Renderer
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest, multiprocess


class PlaintextRenderer(Renderer):
    def render(self, data: http.ResponseData) -> bytes:
        return data


@annotate(renderers=[PlaintextRenderer()])
def expose_metrics():
    return Response(generate_latest(), headers={
        "content-type": CONTENT_TYPE_LATEST,
    })


@annotate(renderers=[PlaintextRenderer()])
def expose_metrics_multiprocess():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), headers={
        "content-type": CONTENT_TYPE_LATEST,
    })
