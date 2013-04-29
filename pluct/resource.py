# -*- coding: utf-8 -*-
import json
import re

from uritemplate import expand
from jsonschema import validate, SchemaError, ValidationError

from pluct.request import Request
from pluct import schema


def add_methods(resource, s, auth=None):
    for link in s.links or []:
        method = link.get("method", "GET")
        href = link.get("href")
        rel = link.get("rel")
        href = expand(href, resource.data)
        method_class = Request(method, href, auth)
        setattr(resource, rel, method_class.process)


def schema_from_header(headers, auth=None):
    p = re.compile(".*profile=([^;]+);?")
    schema_url = p.findall(headers.get('content-type', ''))
    if schema_url:
        return schema.get(schema_url[0], auth)
    return None


class NewResource(object):
    def __init__(self, url, data=None, schema=None, auth=None):
        self.auth = auth
        self.url = url
        self.data = data
        self.schema = schema
        if self.schema:
            add_methods(self, self.schema, self.auth)

    def is_valid(self):
        try:
            validate(self.data, self.schema.__dict__)
        except (SchemaError, ValidationError):
            return False
        return True


def get(url, auth=None):
    response = Request('GET', url, auth).process()
    s = schema_from_header(response.headers, auth)
    return NewResource(
        url=url,
        auth=auth,
        data=response.json(),
        schema=s
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
