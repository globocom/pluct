#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import requests
from uritemplate import expand


def check_valid_response(response):
    return response.status_code == 200 and 'application/json' in response.headers['content-type']


class InvalidSchemaException(Exception):
    pass


class Service(object):
    def __init__(self, url, version=''):
        self.url = os.path.join(url, version)
        self.version = version
        self.auth = {}

        self.resources = self._get_service_resources()

        self._create_resources_attributes()


    def connect(self, auth_type, username, password):
        if auth_type is 'apikey':
            self.auth = {
                'type': auth_type,
                'credentials': '{0}:{1}'.format(username, password)
            }
            self._create_resources_attributes()


    def _get_service_resources(self):
        schema_url = os.path.join(self.url, 'schemas')
        response = requests.get(url=schema_url)
        if check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict['items']
        return None

    def _create_resources_attributes(self):
        if self.resources:
            for resource in self.resources:
                resource_instance = Resource(name=resource['collection_name'], service_url=self.url, auth=self.auth)
                if resource_instance._methods:
                    setattr(self, resource['collection_name'], resource_instance)
        else:
            raise InvalidSchemaException('{0} not have a valid schema'.format(self.url))


class RequestMethod(object):


    def __init__(self, rel, method, href, auth):
        self.rel = rel
        self.method = method
        self.href = href
        self.auth = auth

    def get_headers(self):
        header = {}
        header['content-type'] = 'application/json'
        if self.auth:
            header['Authorization'] = '{0} {1}'.format(self.auth['type'], self.auth['credentials'])

        return header


    @property
    def process(self):
        request_type_by_method = {
            'GET': self._make_get_method,
            'POST': self._make_post_method,
            'PATCH': self._make_patch_method,
            'PUT': self._make_put_method,
            'DELETE': self._make_delete_method
        }
        return request_type_by_method[self.method]

    def get_url(self, resource_id):
        url = expand(self.href, {'resource_id': resource_id})
        return url

    def _make_get_method(self, resource_id=None):
        url = self.get_url(resource_id)
        return requests.get(url=url, headers=self.get_headers())

    def _make_post_method(self, data):
        url = self.href
        return requests.post(url=url, data=json.dumps(data), headers=self.get_headers())

    def _make_patch_method(self, resource_id, data):
        url = self.get_url(resource_id)
        return requests.patch(url=url, data=json.dumps(data), headers=self.get_headers())

    def _make_put_method(self, resource_id, data):
        url = self.get_url(resource_id)
        return requests.put(url=url, data=json.dumps(data), headers=self.get_headers())

    def _make_delete_method(self, resource_id):
        url = self.get_url(resource_id)
        return requests.delete(url=url, headers=self.get_headers())



class Resource(object):

    def __init__(self, name, service_url, auth={}):
        self.auth = auth

        self.schema = self._get_schema(service_url=service_url, resource_name=name)
        self.url = self._get_url()
        self._methods = self._get_allowed_methods()

        self._create_requests_methods(auth)

    def get_headers(self):
        header = {}
        header['content-type'] = 'application/json'
        return header


    def get_request_method(self, link):
        rel = link['rel']
        href = link['href']
        try:
            method = link['method']
        except KeyError:
            method = 'GET'
        return method, rel, href

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
        methods = set()
        if self.schema and 'links' in self.schema:
            for link in self.schema['links']:
                method, rel, href = self.get_request_method(link)
                methods.add(method)
        return methods
