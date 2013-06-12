# -*- coding: utf-8 -*-
import re

from uritemplate import expand
from jsonschema import validate, SchemaError, ValidationError

from pluct.request import Request
from pluct.schema import Schema
from pluct import schema


def add_methods(resource, s, auth=None):
    for link in s.links or []:
        method = link.get("method", "GET")
        href = link.get("href")
        rel = link.get("rel")
        href = expand(href, resource.data)
        method_class = Request(method, href, auth)
        setattr(resource, rel, method_class.process)


def schema_from_header(headers, auth=None):
    p = re.compile(".*profile=([^;]+);?")
    schema_url = p.findall(headers.get('content-type', ''))
    if schema_url:
        return schema.get(schema_url[0], auth)
    return None


class Resource(object):

    def __init__(self, url, data=None, schema=None, auth=None):
        self.auth = auth
        self.url = url
        self.data = data
        self.schema = schema
        if self.schema:
            add_methods(self, self.schema, self.auth)

        self.parse_data()

    def __repr__(self):
        return str(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, attr):
        if attr in self.data:
            return self.data[attr]
        raise KeyError

    def is_valid(self):
        try:
            validate(self.data, self.schema.__dict__)
        except (SchemaError, ValidationError):
            return False
        return True

    def parse_data(self):
        if isinstance(self.data, dict):
            for key, value in self.data.items():
                if isinstance(value, list):
                    data_items = []
                    for item in value:
                        prop_items = self.schema.properties[key]['items']
                        if "$ref" in prop_items:
                            s = schema.get(prop_items['$ref'], self.auth)
                        else:
                            s = Schema(self.url, **prop_items)
                        data_items.append(
                            Resource(
                                self.url,
                                data=item,
                                schema=s,
                            )
                        )
                    self.data[key] = data_items


def get(url, auth=None):
    response = Request('GET', url, auth).process()
    s = schema_from_header(response.headers, auth)
    return Resource(
        url=url,
        auth=auth,
        data=response.json(),
        schema=s
    )
