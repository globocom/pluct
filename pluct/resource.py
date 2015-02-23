# -*- coding: utf-8 -*-

import uritemplate
import jsonpointer
import urlparse

from jsonschema import SchemaError, validate, ValidationError, RefResolver

from pluct import datastructures
from pluct.schema import Schema


class Resource(object):

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            'Use subclasses or Resource.from_data to initialize resources')

    def init(self, url, data=None, schema=None, session=None):
        self.url = url
        self.data = data or self.default_data()
        self.schema = schema
        self.session = session

        self.parse_data()

    def session_request_json(self, url):
        return self.session.request(url).json()

    def is_valid(self):
        handlers = {'https': self.session_request_json,
                    'http': self.session_request_json}
        resolver = RefResolver.from_schema(self.schema.raw_schema,
                                           handlers=handlers)
        try:
            validate(self.data, self.schema.raw_schema, resolver=resolver)
        except (SchemaError, ValidationError):
            return False
        return True

    def rel(self, name, **kwargs):
        link = self.schema.get_link(name)
        method = link.get('method', 'get')
        href = link.get('href', '')

        params = kwargs.get('params', {})

        variables = uritemplate.variables(href)

        uri = self.expand_uri(name, **params)

        if not urlparse.urlparse(uri).netloc:
            uri = urlparse.urljoin(self.url, uri)

        if 'params' in kwargs:
            unused_params = {
                k: v for k, v in params.items() if k not in variables}
            kwargs['params'] = unused_params

        return self.session.resource(uri, method=method, **kwargs)

    def has_rel(self, name):
        link = self.schema.get_link(name)
        return bool(link)

    def expand_uri(self, name, **kwargs):
        link = self.schema.get_link(name)
        href = link.get('href', '')

        context = dict(self.data, **kwargs)

        return uritemplate.expand(href, context)

    @classmethod
    def from_data(cls, url, data=None, schema=None, session=None):
        if isinstance(data, (list, tuple)):
            klass = ArrayResource
        elif isinstance(data, dict):
            klass = ObjectResource
        else:
            return data

        return klass(
            url, data=data, schema=schema, session=session)

    @classmethod
    def from_response(cls, response, session, schema):
        try:
            data = response.json()
        except ValueError:
            data = {}
        return cls.from_data(
            url=response.url,
            data=data,
            session=session,
            schema=schema
        )

    def parse_data(self):
        for key, value in self.iterate_items():
            schema = self.item_schema(key)
            self.data[key] = self.from_data(
                self.url, data=value, schema=schema, session=self.session)

    def resolve_pointer(self, *args, **kwargs):
        return jsonpointer.resolve_pointer(self.data, *args, **kwargs)


class ObjectResource(datastructures.IterableUserDict, Resource, dict):

    SCHEMA_PREFIX = 'properties'

    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

    def default_data(self):
        return {}

    def iterate_items(self):
        return self.data.iteritems()

    def item_schema(self, key):
        href = '#/{0}/{1}'.format(self.SCHEMA_PREFIX, key)
        return Schema(href, raw_schema=self.schema, session=self.session)

    def __ne__(self, other):
        return self.data != other

    def __eq__(self, other):
        return self.data == other


class ArrayResource(datastructures.UserList, Resource, list):

    SCHEMA_PREFIX = 'items'

    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

    def default_data(self):
        return []

    def iterate_items(self):
        return enumerate(self.data)

    def item_schema(self, key):
        href = '#/{0}'.format(self.SCHEMA_PREFIX)
        return Schema(href, raw_schema=self.schema, session=self.session)
