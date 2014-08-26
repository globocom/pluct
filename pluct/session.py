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

    def resource(self, url, **kwargs):
        response = self.request(url, **kwargs)
        schema = None

        schema_url = get_profile_from_header(response.headers)
        if schema_url is not None:
            schema = LazySchema(href=schema_url, session=self)

        return Resource.from_response(
            response=response, session=self, schema=schema)

    def schema(self, url, **kwargs):
        data = self.request(url, **kwargs).json()
        return Schema(url, raw_schema=data, session=self)

    def request(self, url, **kwargs):
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('content-type', 'application/json')

        kwargs.setdefault('method', 'get')

        response = self.client.request(url=url, **kwargs)
        response.raise_for_status()

        return response
