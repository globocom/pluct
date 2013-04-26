# -*- coding: utf-8 -*-
import json
import os
import re

from pluct.requestmethod import RequestMethod
from pluct import schema


class Resource(object):

    def __init__(self, url, auth={}):
        self.auth = auth
        self.url = url
        self._methods = self._get_allowed_methods()
        self._create_requests_methods(auth)

    @property
    def _response(self):
        request = RequestMethod(rel='get', method='GET', href=self.url, auth=self.auth)
        return request.process()

    @property
    def data(self):
        return self._response.json

    @property
    def schema(self):
        p = re.compile(".*profile=([^;]+);?")
        schema_url = p.findall(self._response.headers.get('content-type', ''))
        if schema_url:
            return schema.get(schema_url[0])
        return self._get_schema()

    def _create_requests_methods(self, auth):
        if self.schema and 'links' in self.schema:
            for link in self.schema['links']:
                method, rel, href = self.get_request_method(link)
                method_class = RequestMethod(rel, method, href, auth)
                setattr(self, rel, method_class.process)

    def _get_schema(self):
        method = RequestMethod(rel='get', method='GET', href=self.url, auth=self.auth)
        response = method.process()
        if RequestMethod.check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict
        return None

    def _get_allowed_methods(self):
        methods = set()
        if self.schema and 'links' in self.schema:
            for link in self.schema['links']:
                method, rel, href = self.get_request_method(link)
                methods.add(method)
        return methods

    def get_request_method(self, link):
        rel = link['rel']
        href = link['href']
        method = link.get('method', 'GET')
        return method, rel, href
