#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from pluct.requestmethod import RequestMethod


class Resource(object):

    def __init__(self, name, service_url, auth={}):
        self.auth = auth
        self.schema = self._get_schema(service_url=service_url, resource_name=name)
        self._url = os.path.join(service_url, name)
        self.url = self._get_url()
        self._methods = self._get_allowed_methods()
        self._create_requests_methods(auth)

    @property
    def data(self):
        request = RequestMethod(rel='get', method='GET', href=self._url, auth=self.auth)
        response = request.process()
        return response.json

    def _create_requests_methods(self, auth):
        if self.schema and 'links' in self.schema:
            for link in self.schema['links']:
                method, rel, href = self.get_request_method(link)
                method_class = RequestMethod(rel, method, href, auth)
                setattr(self, rel, method_class.process)

    def _get_schema(self, service_url, resource_name):
        schema_url = os.path.join(service_url, resource_name)
        method = RequestMethod(rel='get', method='GET', href=schema_url, auth=self.auth)
        response = method.process()
        if RequestMethod.check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict
        return None

    def _get_url(self):
        if self.schema and 'links' in self.schema:
            for link in self.schema['links']:
                if link['rel'] == 'self':
                    return link['href']

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
