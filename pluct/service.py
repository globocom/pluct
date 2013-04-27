#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from pluct.request import Request
from pluct.resource import Resource


class InvalidSchemaException(Exception):
    pass


class Service(object):
    def __init__(self, url, version=''):
        self.url = os.path.join(url, version)
        self.version = version
        self.auth = {}

        self.resources = self._get_service_resources()

        self._create_resources_attributes()

    def _get_service_resources(self):
        schema_url = os.path.join(self.url, 'schemas')
        method = Request(method='GET', href=schema_url, auth=self.auth)
        response = method.process()

        if Request.check_valid_response(response):
            resource_dict = json.loads(response.content)
            return resource_dict['items']
        return None

    def _create_resources_attributes(self):
        if self.resources:
            for resource in self.resources:
                resource_instance = Resource(
                    name=resource['collection_name'],
                    service_url=self.url, auth=self.auth
                )
                if resource_instance._methods:
                    setattr(self, resource['collection_name'],
                            resource_instance)
        else:
            raise InvalidSchemaException(
                '{0} not have a valid schema'.format(self.url)
            )

    def connect(self, auth_type, username, password):
        if auth_type is 'apikey':
            self.auth = {
                'type': auth_type,
                'credentials': '{0}:{1}'.format(username, password)
            }
            self._create_resources_attributes()
