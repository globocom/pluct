# -*- coding: utf-8 -*-


import re

import requests


class Schema(object):
    def __init__(self, url, type=None, title=None, required=None,
                 properties=None, links=None):
        self.url = url
        self.type = type
        if required:
            self.required = required
        self.title = title
        if properties:
            self.properties = properties
        if links:
            self.links = links


def get(url, auth=None):
    headers = {
        'content-type': 'application/json'
    }
    if auth:
        headers['Authorization'] = '{0} {1}'.format(
            auth['type'], auth['credentials']
        )
    data = requests.get(url, headers=headers).json()
    return Schema(
        url=url,
        type=data.get("type"),
        required=data.get("required"),
        title=data.get("title"),
        properties=data.get("properties"),
        links=data.get("links")
    )


def from_header(headers, auth=None):
    p = re.compile(".*profile=([^;]+);?")
    schema_url = p.findall(headers.get('content-type', ''))
    if schema_url:
        return get(schema_url[0], auth)
    return None
