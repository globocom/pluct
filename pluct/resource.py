# -*- coding: utf-8 -*-
import json
import re

from pluct.request import Request
from pluct import schema


def add_methods(resource, s, auth=None):
    for link in s.links or []:
        method = link.get("method", "GET")
        href = link.get("href")
        rel = link.get("rel")
        method_class = Request(method, href, auth)
        setattr(resource, rel, method_class.process)


def schema_from_header(headers):
    p = re.compile(".*profile=([^;]+);?")
    schema_url = p.findall(headers.get('content-type', ''))
    if schema_url:
        return schema.get(schema_url[0])
    return None


class NewResource(object):
    def __init__(self, url, auth=None):
        self.auth = auth
        self.url = url
        self._data = None

    @property
    def data(self):
        if not self._data:
            response = Request('GET', self.url, self.auth).process()
            s = schema_from_header(response.headers)
            if s:
                self.schema = s
                add_methods(self, s)
            self._data = response.json()
        return self._data


def get(url, auth=None):
    return NewResource(
        url=url
    )


class Resource(object):
    def __init__(self, url, auth={}):
        self.auth = auth
        self.url = url
        self._response = None
        self._data = None
        self._schema = None
        self._methods = self._get_allowed_methods()
        self._create_requests_methods(auth)

    @property
    def response(self):
        if not self._response:
            request = Request(method='GET', href=self.url, auth=self.auth)
            self._response = request.process()
        return self._response

    @property
    def data(self):
        if not self._data:
            self._data = self.response.json
        return self._data

    @property
    def schema(self):
        if not self._schema:
            _schema = schema_from_header(self.response.headers)
            if _schema:
                self._schema = _schema
            else:
                self._schema = self._get_schema()
        return self._schema

    def _create_requests_methods(self, auth):
        for link in self.schema.get('links', []):
            method, rel, href = self.get_request_method(link)
            method_class = Request(method, href, auth)
            setattr(self, rel, method_class.process)

    def _get_schema(self):
        if Request.check_valid_response(self.response):
            resource_dict = json.loads(self.response.content)
            return resource_dict
        return None

    def _get_allowed_methods(self):
        methods = set()
        for link in self.schema.get('links', []):
            method, rel, href = self.get_request_method(link)
            methods.add(method)
        return methods

    def get_request_method(self, link):
        rel = link['rel']
        href = link['href']
        method = link.get('method', 'GET')
        return method, rel, href
