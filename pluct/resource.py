# -*- coding: utf-8 -*-

import requests
import uritemplate
from jsonschema import SchemaError, validate, ValidationError

from pluct import schema
from pluct.schema import Schema
from request import from_response


class Resource(dict):

    def __init__(self, url, data=None, schema=None,
                 response=None, timeout=30, session=None):
        self.url = url
        self.data = data
        self.schema = schema
        self.timeout = timeout
        self.response = response
        if self.schema and self.is_valid():
            self.parse_data()

        self.session = session

    def __str__(self):
        return str(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, attr):
        if attr in self.data:
            return self.data[attr]
        raise KeyError

    def __contains__(self, item):
        return dict.__contains__(self.data, item)

    def is_valid(self):
        try:
            validate(self.data, self.schema._raw_schema)
        except (SchemaError, ValidationError):
            return False
        return True

    def parse_data(self):
        if not isinstance(self.data, dict):
            return

        for key, value in self.data.items():
            if not isinstance(value, list):
                continue

            item_schema = self.schema.properties.get(key, {})
            is_array = item_schema.get('type') == 'array'

            if not is_array:
                continue

            data_items = []
            prop_items = item_schema.get('items', {})

            if "$ref" in prop_items:
                s = schema.get(prop_items['$ref'])
            else:
                s = Schema(self.url, prop_items)

            for item in value:
                if not isinstance(item, dict):
                    data_items.append(item)
                    continue

                data_items.append(
                    Resource(
                        self.url,
                        data=item,
                        schema=s,
                    )
                )

            self.data[key] = data_items

    def rel(self, name, **kwargs):
        link = self.get_rel(name)
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

    def get_rel(self, name):
        for link in getattr(self.schema, "links", []) or []:
            if link.get('rel') == name:
                return link
        return None


def get(url, *args, **kwargs):
    response = requests.get(url, *args, **kwargs)
    return from_response(Resource, response)
