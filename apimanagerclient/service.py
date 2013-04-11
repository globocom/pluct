#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import requests


def check_valid_response(response):
    return response.status_code == 200 and 'application/json' in response.headers['content-type']

class InvalidSchemaException(Exception):
    pass


class Service(object):
    def __init__(self, url, version):
        self.url = os.path.join(url, version)
        self.version = version

        schema_url = os.path.join(self.url, 'schemas')
        self.resources = self._get_service_resources(schema_url)

        self._create_resources_attributes()

    def _get_service_resources(self, schema_url):
        response = requests.get(url=schema_url)
        if check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict['items']
        return None
    
    def _create_resources_attributes(self):
        if self.resources:
            for resource in self.resources:
                resource_instance = Resource(name=resource['collection_name'], service_url=self.url)
                self.__setattr__(resource['collection_name'], resource_instance)
        else:
            raise InvalidSchemaException('{0} not have a valid schema'.format(self.url))


class Resource(object):

    def __init__(self, name, service_url):
        self.url = os.path.join(service_url, name)
        self.methods = self._get_allowed_methods()

    def _get_schema(self):
        schema_url = os.path.join(self.url, 'schema')
        response = requests.get(url=schema_url)
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
        response = requests.get(url=self.url)
        if check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict['items']

        return []
