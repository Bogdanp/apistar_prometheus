import pytest

from apistar import App, Route
from apistar.test import TestClient
from apistar_prometheus import PrometheusComponent, PrometheusHooks, expose_metrics


def index():
    return {}


def fail():
    raise RuntimeError("fail")


routes = [
    Route("/", method="GET", handler=index),
    Route("/fail", method="GET", handler=fail),
    Route("/metrics", method="GET", handler=expose_metrics),
]

components = [
    PrometheusComponent(),
]

event_hooks = [
    PrometheusHooks(),
]

app = App(
    routes=routes,
    components=components,
    event_hooks=event_hooks,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_can_track_metrics(client):
    # Given an apistar app client
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


def test_can_track_metrics_for_endpoints_that_fail(client):
    # Given an apistar app client
    # When I visit an endpoint that raises an unhandled error
    with pytest.raises(RuntimeError):
        client.get("/fail")

    # And then visit the metrics endpoint
    response = client.get("/metrics")

    # Then the response should succeed
    assert response.status_code == 200

    # And it should contain a metric for the first request
    assert b'http_requests_total{code="500",handler="tests.test_metrics.fail",method="GET"} 1.0' \
        in response.content


def test_can_track_metrics_for_builtin_endpoints(client):
    # Given an apistar app client
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
