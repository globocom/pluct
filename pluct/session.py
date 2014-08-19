# -*- coding: utf-8 -*-

from requests import Session as RequestsSession

from pluct.resource import Resource
from pluct.schema import Schema, LazySchema, get_profile_from_header


class Session(object):

    def __init__(self, client=None, timeout=None):
        self.timeout = timeout
        self.store = {}

        if client is None:
            self.client = RequestsSession()
        else:
            self.client = client

    def resource(self, url, *args, **kwargs):
        response = self.request('get', url, *args, **kwargs)
        schema_url = get_profile_from_header(response.headers)
        schema = LazySchema(url=schema_url, session=self)

        return Resource.from_response(
            response=response, session=self, schema=schema)

    def schema(self, url, *args, **kwargs):
        data = self.request('get', url, *args, **kwargs).json()
        return Schema(url, raw_schema=data, session=self)

    def request(self, method, url, *args, **kwargs):
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('content-type', 'application/json')

        response = self.client.request(method, url, *args, **kwargs)

        return response
