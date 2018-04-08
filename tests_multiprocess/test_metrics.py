import os

dir_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "prom")
os.makedirs(dir_path, exist_ok=True)
os.environ["prometheus_multiproc_dir"] = dir_path

from apistar import App, Route
from apistar.test import TestClient
from apistar_prometheus import PrometheusComponent, PrometheusHooks, expose_metrics_multiprocess


def index():
    return {}


components = [
    PrometheusComponent(),
]

routes = [
    Route("/", method="GET", handler=index),
    Route("/metrics", method="GET", handler=expose_metrics_multiprocess),
]

event_hooks = [
    PrometheusHooks(),
]

app = App(
    routes=routes,
    components=components,
    event_hooks=event_hooks,
)


def test_can_track_metrics():
    # Given an apistar app client
    client = TestClient(app)

    # When I visit an endpoint
    response = client.get("/")
    assert response.status_code == 200

    # And then visit the metrics endpoint
    response = client.get("/metrics")

    # Then the response should succeed
    assert response.status_code == 200

    # And it should contain a metric for the first request
    assert b'http_requests_total{code="200",handler="tests_multiprocess.test_metrics.index",method="GET"}' \
        in response.content
