#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests


class Resource(object):

    def __init__(self, name, service_url):
        self.url = "{0}/{1}".format(service_url, name)
        self.methods = self.get_allowed_methods()

    def _get_schema(self):
        schema_url = '{0}/{1}'.format(self.url, 'schema')
        response = requests.get(url=schema_url, params={'format': 'json'})
        resource_dict = json.loads(response.content)
        return resource_dict

    def get_allowed_methods(self):
        schema = self._get_schema()
        return schema['allowed_list_http_methods']


class Service(object):
    def __init__(self, url, version):
        self.url = url
        self.version = version
        schema_url = "{0}/{1}".format(url, version)
        self.resources = self._get_service_resources(schema_url)
        self._create_resources_attributes()

    def _get_service_resources(self, schema_url):
        response = requests.get(url=schema_url, params={'format': 'json'})
        resource_dict = json.loads(response.content)
        return resource_dict

    def _create_resources_attributes(self):
        for key, value in self.resources.items():
            self.__setattr__(key, Resource(name=key, service_url=self.url))
