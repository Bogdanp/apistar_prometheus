import os

from setuptools import setup


def rel(*xs):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *xs)


with open(rel("apistar_prometheus", "__init__.py"), "r") as f:
    version_marker = "__version__ = "
    for line in f:
        if line.startswith(version_marker):
            _, version = line.split(version_marker)
            version = version.strip().strip('"')
            break
    else:
        raise RuntimeError("Version marker not found.")


setup(
    name="apistar_prometheus",
    version=version,
    description="A Prometheus component for API Star.",
    long_description="Visit https://github.com/Bogdanp/apistar_prometheus for more information.",
    packages=["apistar_prometheus"],
    include_package_data=True,
    install_requires=[
        "apistar>=0.3",
        "prometheus-client>=0.0.20",
    ],
)
