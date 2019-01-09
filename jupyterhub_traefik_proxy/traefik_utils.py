import sys
import json
import re

from urllib.parse import urlparse


def generate_rule(routespec):
    if routespec.startswith("/"):
        # Path-based route, e.g. /proxy/path/
        rule = "PathPrefix:" + routespec
    else:
        # Host-based routing, e.g. host.tld/proxy/path/
        host, path_prefix = routespec.split("/", 1)
        path_prefix = "/" + path_prefix
        rule = "Host:" + host + ";PathPrefix:" + path_prefix
    return rule


def generate_alias(url, server_type=""):
    return server_type + re.sub("[.:/]", "_", (urlparse(url).netloc))


def generate_backend_entry(
    proxy, backend_alias, separator="/", url=False, weight=False
):
    backend_entry = ""
    if separator is "/":
        backend_entry = proxy.etcd_traefik_prefix
    backend_entry += (
        "backends"
        + separator
        + backend_alias
        + separator
        + "servers"
        + separator
        + "server1"
    )
    if url is True:
        backend_entry += separator + "url"
    elif weight is True:
        backend_entry += separator + "weight"

    return backend_entry


def generate_frontend_backend_entry(proxy, frontend_alias):
    return proxy.etcd_traefik_prefix + "frontends/" + frontend_alias + "/backend"


def generate_frontend_rule_entry(proxy, frontend_alias, separator="/"):
    frontend_rule_entry = (
        "frontends"
        + separator
        + frontend_alias
        + separator
        + "routes"
        + separator
        + "test"
    )
    if separator == "/":
        frontend_rule_entry = (
            proxy.etcd_traefik_prefix + frontend_rule_entry + separator + "rule"
        )

    return frontend_rule_entry


def generate_route_keys(proxy, target, routespec, separator=""):
    backend_alias = generate_alias(target, "backend")
    frontend_alias = generate_alias(target, "frontend")

    if separator != ".":
        backend_url_path = generate_backend_entry(proxy, backend_alias, url=True)
        frontend_rule_path = generate_frontend_rule_entry(proxy, frontend_alias)
        backend_weight_path = generate_backend_entry(proxy, backend_alias, weight=True)
        frontend_backend_path = generate_frontend_backend_entry(proxy, frontend_alias)
        return (
            backend_alias,
            backend_url_path,
            backend_weight_path,
            frontend_alias,
            frontend_backend_path,
            frontend_rule_path,
        )

    backend_url_path = generate_backend_entry(proxy, backend_alias, separator=separator)
    frontend_rule_path = generate_frontend_rule_entry(
        proxy, frontend_alias, separator=separator
    )

    return (backend_alias, backend_url_path, frontend_alias, frontend_rule_path)
