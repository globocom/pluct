# -*- coding: utf-8 -*-


from cgi import parse_header

from pluct.datastructures import IterableUserDict


class Schema(IterableUserDict):

    def __init__(self, url, raw_schema=None):
        self.url = url
        self.data = raw_schema

    @property
    def raw_schema(self):
        return self.data

    @classmethod
    def from_response(cls, response):
        return cls(response.url, raw_schema=response.json())


def get_profile_from_header(headers):
    if 'content-type' not in headers:
        return None

    full_content_type = 'content-type: {0}'.format(headers['content-type'])
    header, parameters = parse_header(full_content_type)

    if 'profile' not in parameters:
        return None

    schema_url = parameters['profile']
    return schema_url
