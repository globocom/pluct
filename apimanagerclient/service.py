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
        self.schema = self._get_schema(service_url=service_url, resource_name=name)
        self.url = self._get_url()
        self._methods = self._get_allowed_methods()
        self._create_requests_methods()

    def _make_post_method(self, data):
        return requests.post(self.url, json.dumps(data), headers={'content-type': 'application/json'})

    def _create_requests_methods(self):
        if 'POST' in self._methods.keys():
            self.__setattr__('create', self._make_post_method)





    def _get_schema(self, service_url, resource_name):
        schema_url = os.path.join(service_url, resource_name)
        response = requests.get(url=schema_url)

        if check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict
        return None

    def _get_url(self):
        if self.schema and 'links' in self.schema:
            for link in self.schema['links']:
                if link['rel'] == 'self':
                    return link['href']

    def _get_allowed_methods(self):
        methods = {}
        if self.schema and 'links' in self.schema:
            for link in self.schema['links']:
                if 'method' in link:
                    methods[link['method']] = link['rel']
        return methods

    def __call__(self, *args, **kwargs):
        response = requests.get(url=self.url)
        if check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict['items']

        return []
