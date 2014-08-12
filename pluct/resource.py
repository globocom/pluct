# -*- coding: utf-8 -*-

import uritemplate
from jsonschema import SchemaError, validate, ValidationError

from pluct import datastructures
from pluct.schema import Schema, LazySchema


class Resource(object):

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            'Use subclasses or Resource.from_data to initialize resources')

    def init(self, url, data=None, schema=None, session=None):
        self.url = url
        self.data = data or self.default_data()
        self.schema = schema
        self.session = session

        if self.schema and self.is_valid():
            self.parse_data()

    def is_valid(self):
        try:
            validate(self.data, self.schema.raw_schema)
        except (SchemaError, ValidationError):
            return False
        return True

    def parse_data(self):
        if not isinstance(self.data, dict):
            return

        for key, value in self.data.items():
            if not isinstance(value, list):
                continue

            item_schema = self.schema['properties'].get(key, {})
            is_array = item_schema.get('type') == 'array'

            if not is_array:
                continue

            data_items = []
            prop_items = item_schema.get('items', {})

            if "$ref" in prop_items:
                s = LazySchema(prop_items['$ref'], session=self.session)
            else:
                s = Schema(self.url, prop_items, session=self.session)

            for item in value:
                if not isinstance(item, dict):
                    data_items.append(item)
                    continue

                data_items.append(
                    ObjectResource(
                        self.url,
                        data=item,
                        schema=s,
                        session=self.session,
                    )
                )

            self.data[key] = data_items

    def rel(self, name, **kwargs):
        link = self.schema.get_link(name)
        method = link.get('method', 'get')
        href = link.get('href', '')

        params = kwargs.get('params', {})
        context = dict(self.data, **params)

        variables = uritemplate.variables(href)
        uri = uritemplate.expand(href, context)

        if 'params' in kwargs:
            unused_params = {
                k: v for k, v in params.items() if k not in variables}
            kwargs['params'] = unused_params

        return self.session.request(method, uri, **kwargs)

    @classmethod
    def from_data(cls, url, data=None, schema=None, session=None):
        klass = ObjectResource
        if isinstance(data, (list, tuple)):
            klass = ArrayResource

        return klass(
            url, data=data, schema=schema, session=session)

    @classmethod
    def from_response(cls, response, session, schema):
        try:
            data = response.json()
        except ValueError:
            data = None
        return cls.from_data(
            url=response.url,
            data=data,
            session=session,
            schema=schema
        )


class ObjectResource(datastructures.IterableUserDict, Resource):

    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

    def default_data(self):
        return {}


class ArrayResource(datastructures.UserList, Resource):

    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

    def default_data(self):
        return []
