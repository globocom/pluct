# -*- coding: utf-8 -*-

import uritemplate
from jsonschema import SchemaError, validate, ValidationError

from pluct.datastructures import IterableUserDict
from pluct.schema import Schema, LazySchema


class Resource(IterableUserDict):

    def __init__(self, url, data=None, schema=None, session=None):
        self.url = url
        self.data = data
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
                    Resource(
                        self.url,
                        data=item,
                        schema=s,
                        session=self.session,
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
        links = self.schema.get('links') or []
        for link in links:
            if link.get('rel') == name:
                return link
        return None

    @classmethod
    def from_response(cls, response, session):
        try:
            data = response.json()
        except ValueError:
            data = {}
        return cls(
            url=response.url,
            data=data,
            session=session,
        )
