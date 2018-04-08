# apistar_prometheus

[![Build Status](https://travis-ci.org/Bogdanp/apistar_prometheus.svg?branch=master)](https://travis-ci.org/Bogdanp/apistar_prometheus)
[![Test Coverage](https://api.codeclimate.com/v1/badges/bf3853435dc643c96208/test_coverage)](https://codeclimate.com/github/Bogdanp/apistar_prometheus/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/bf3853435dc643c96208/maintainability)](https://codeclimate.com/github/Bogdanp/apistar_prometheus/maintainability)
[![PyPI version](https://badge.fury.io/py/apistar-prometheus.svg)](https://badge.fury.io/py/apistar-prometheus)

[Prometheus] metrics for [API Star] apps.


## Requirements

* [API Star] 0.4+
* [prometheus_client] 0.0.20+


## Installation

Use [pipenv] (or plain pip) to install the package:

    pipenv install apistar_prometheus

To hook it into your app, add the `Prometheus` component to your app's
`components` list, add a route for the `expose_metrics` handler and
add `before_request` and `after_request` as the first and last hooks,
respectively.

``` python
from apistar import App, Route
from apistar_prometheus import PrometheusComponent, PrometheusHooks, expose_metrics

routes = [
    # ...
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
```

### Multiprocess mode

The default configuration assumes a single multi-threaded worker
process.  To expose metrics in a multiprocess configuration (eg. using
gunicorn), set the `prometheus_multiprocess_dir` environment variable
and use the `expose_metrics_multiprocess` handler.

``` python
from apistar_prometheus import PrometheusComponent, PrometheusHooks, expose_metrics_multiprocess

routes = [
    # ...,
    Route("/metrics", method="GET", handler=expose_metrics_multiprocess),
]
```


## License

apistar_prometheus is licensed under Apache 2.0.  Please see [LICENSE]
for licensing details.


[Prometheus]: https://prometheus.io/
[API Star]: https://github.com/encode/apistar/
[pipenv]: https://docs.pipenv.org
[prometheus_client]: https://github.com/prometheus/client_python
[LICENSE]: https://github.com/Bogdanp/apistar_prometheus/blob/master/LICENSE
