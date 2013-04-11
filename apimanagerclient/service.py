#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests


def check_valid_response(response):
    return response.status_code == 200 and 'application/json' in response.headers['content-type']

class InvalidSchemaException(Exception):
    pass


class Service(object):
    def __init__(self, url, version):
        self.url = "{0}/{1}".format(url, version)
        self.version = version
        self.resources = self._get_service_resources(self.url)
        self._create_resources_attributes()

    def _get_service_resources(self, schema_url):
        response = requests.get(url=schema_url, params={'format': 'json'})
        if check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict
        return None
    
    def _create_resources_attributes(self):
        if self.resources:
            for key, value in self.resources.items():
                resource = Resource(name=key, service_url=self.url)
                if resource.methods:
                    self.__setattr__(key, resource)
        else:
            raise InvalidSchemaException('{0} not have a valid schema'.format(self.url))


class Resource(object):

    def __init__(self, name, service_url):
        self.url = "{0}/{1}".format(service_url, name)
        self.methods = self._get_allowed_methods()

    def _get_schema(self):
        schema_url = '{0}/{1}'.format(self.url, 'schema')
        response = requests.get(url=schema_url, params={'format': 'json'})
        if check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict
        return None

    def _get_allowed_methods(self):
        schema = self._get_schema()
        if schema and 'allowed_list_http_methods' in schema:
            return schema['allowed_list_http_methods']
        return []

    def all(self):
        if 'get' in self.methods:
            response = requests.get(url=self.url)
            if check_valid_response(response):
                resource_dict = json.loads(response.content)
                return resource_dict['objects']
        return []
