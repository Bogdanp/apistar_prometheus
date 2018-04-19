import pytest

from apistar import App, Route, exceptions, http
from apistar.test import TestClient
from apistar_prometheus import PrometheusComponent, PrometheusHooks, expose_metrics


class AuthenticationHooks:
    def on_request(self, route: Route) -> None:
        if route.handler is auth_required:
            raise exceptions.Forbidden({"message": "forbidden"})


def index():
    return {}


def bad_request():
    raise exceptions.BadRequest({"message": "bad request"})


def fail():
    raise RuntimeError("fail")


def auth_required():
    return {}


def explicit_response():
    return http.Response(b"hello", headers={"content-type": "text/plain"})


routes = [
    Route("/", method="GET", handler=index),
    Route("/bad-request", method="GET", handler=bad_request),
    Route("/fail", method="GET", handler=fail),
    Route("/auth-required", method="GET", handler=auth_required),
    Route("/explicit", method="GET", handler=explicit_response),
    Route("/metrics", method="GET", handler=expose_metrics),
]

components = [
    PrometheusComponent(),
]

event_hooks = [
    PrometheusHooks(),
    AuthenticationHooks(),
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


def test_can_track_metrics_for_endpoints_that_fail_with_handled_errors(client):
    # Given an apistar app client
    # When I visit an endpoint that raises an apistar exception
    response = client.get("/bad-request")
    assert response.status_code == 400

    # And then visit the metrics endpoint
    response = client.get("/metrics")

    # Then the response should succeed
    assert response.status_code == 200

    # And it should contain a metric for the first request
    assert b'http_requests_total{code="400",handler="tests.test_metrics.bad_request",method="GET"} 1.0' \
        in response.content


def test_can_track_metrics_for_endpoints_that_fail_in_hooks(client):
    # Given an apistar app client
    # When I visit an endpoint that raises an error in a request hook
    response = client.get("/auth-required")
    assert response.status_code == 403

    # And then visit the metrics endpoint
    response = client.get("/metrics")

    # Then the response should succeed
    assert response.status_code == 200

    # And it should contain a metric for the first request
    assert b'http_requests_total{code="403",handler="tests.test_metrics.auth_required",method="GET"} 1.0' \
        in response.content


def test_can_track_metrics_for_endpoints_that_return_explicit_responses(client):
    # Given an apistar app client
    # When I visit an endpoint that returns a Response object
    response = client.get("/explicit")
    assert response.status_code == 200

    # And then visit the metrics endpoint
    response = client.get("/metrics")

    # Then the response should succeed
    assert response.status_code == 200

    # And it should contain a metric for the first request
    assert b'http_requests_total{code="200",handler="tests.test_metrics.explicit_response",method="GET"} 1.0' \
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
