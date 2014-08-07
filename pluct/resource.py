# -*- coding: utf-8 -*-
import requests

from jsonschema import validate, SchemaError, ValidationError

from pluct import schema
from pluct.request import Request
from pluct.schema import Schema
from request import from_response


class Resource(dict):

    def __init__(self, url, data=None, schema=None,
                 auth=None, response=None, timeout=30):
        self.auth = auth
        self.url = url
        self.data = data
        self.schema = schema
        self.timeout = timeout
        self.response = response
        if self.schema and self.is_valid():
            self.parse_data()

    def __getattr__(self, name):
        for link in getattr(self.schema, "links", []) or []:
            method = link.get("method", "GET")
            href = link.get("href")
            if link.get('rel') == name:
                method_class = Request(method, href, self.auth, self)
                return method_class.process
        return super(Resource, self).__getattribute__(name)

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
                s = schema.get(prop_items['$ref'], self.auth)
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


def get(url, auth=None, timeout=30):
    headers = {'content-type': 'application/json'}
    if auth:
        headers['Authorization'] = '{0} {1}'.format(
            auth['type'], auth['credentials']
        )
    response = requests.get(url, headers=headers, timeout=timeout)
    return from_response(Resource, response, auth)
