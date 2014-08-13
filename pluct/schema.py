# -*- coding: utf-8 -*-


from cgi import parse_header
from jsonpointer import resolve_pointer

from pluct.datastructures import IterableUserDict


class Schema(IterableUserDict):

    def __init__(self, href, raw_schema=None, session=None):
        self._init_href(href)

        self.data = resolve_pointer(raw_schema, self.pointer)
        self.session = session

    @property
    def raw_schema(self):
        return self.data

    def get_link(self, name):
        links = self.get('links') or []
        for link in links:
            if link.get('rel') == name:
                return link
        return None

    def _init_href(self, href):
        parts = href.split('#', 1)
        self.url = parts[0]

        self.pointer = ''
        if len(parts) > 1:
            self.pointer = parts[1] or self.pointer

        self.href = '#'.join((self.url, self.pointer))


class LazySchema(Schema):

    def __init__(self, href, session=None):
        self._init_href(href)
        self.session = session
        self._data = None

    @property
    def data(self):
        if self._data is None:
            response = self.session.request('get', self.url)
            data = response.json()
            self._data = resolve_pointer(data, self.pointer)

        return self._data


def get_profile_from_header(headers):
    if 'content-type' not in headers:
        return None

    full_content_type = 'content-type: {0}'.format(headers['content-type'])
    header, parameters = parse_header(full_content_type)

    if 'profile' not in parameters:
        return None

    schema_url = parameters['profile']
    return schema_url
