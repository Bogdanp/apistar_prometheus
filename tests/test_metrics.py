import apistar_prometheus

from apistar import Component, Route, hooks
from apistar.frameworks.wsgi import WSGIApp as App
from apistar.test import TestClient


def index():
    return {}


components = [
    Component(apistar_prometheus.Prometheus, preload=True),
]

routes = [
    Route("/", "GET", index),
    Route("/metrics", "GET", apistar_prometheus.expose_metrics),
]

settings = {
    "BEFORE_REQUEST": [
        apistar_prometheus.before_request,
        hooks.check_permissions,
    ],
    "AFTER_REQUEST": [
        hooks.render_response,
        apistar_prometheus.after_request,
    ],
}

app = App(
    components=components,
    routes=routes,
    settings=settings,
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
    assert b'http_requests_total{code="200",handler="tests.test_metrics.index",method="GET"} 1.0' \
        in response.content


def test_can_track_metrics_for_builtin_endpoints():
    # Given an apistar app client
    client = TestClient(app)

    # When I visit an endpoint that doesn't exist
    response = client.get("/idontexist")
    assert response.status_code == 404

    # And then visit the metrics endpoint
    response = client.get("/metrics")

    # Then the response should succeed
    assert response.status_code == 200

    # And it should contain a metric for the first request
    assert b'http_requests_total{code="404",handler="<builtin>",method="GET"} 1.0' \
        in response.content
