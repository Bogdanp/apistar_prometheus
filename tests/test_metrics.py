from apistar import App, Route
from apistar.test import TestClient
from apistar_prometheus import PrometheusComponent, PrometheusHooks, expose_metrics


def index():
    return {}


routes = [
    Route("/", method="GET", handler=index),
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
