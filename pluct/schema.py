# -*- coding: utf-8 -*-


from cgi import parse_header

from pluct.datastructures import IterableUserDict


class Schema(IterableUserDict):

    def __init__(self, href, raw_schema=None, session=None):
        self.href = href
        self.url = href

        self.data = raw_schema
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


class LazySchema(Schema):

    def __init__(self, url, session=None):
        self.url = url
        self.session = session
        self._data = None

    @property
    def data(self):
        if self._data is None:
            response = self.session.request('get', self.url)
            data = response.json()
            self._data = data

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
