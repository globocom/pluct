# -*- coding: utf-8 -*-


from cgi import parse_header
import requests


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def recursive_wrap(pydict):
    if not isinstance(pydict, dict):
        return pydict
    return AttrDict({k: recursive_wrap(v) for k, v in pydict.items()})


class Schema(object):

    def __init__(self, url, raw_schema=None):
        object.__setattr__(self, 'url', url)
        _schema = None if raw_schema is None else recursive_wrap(raw_schema)
        object.__setattr__(self, '_raw_schema', _schema)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        dict.__setitem__(self._raw_schema, key, recursive_wrap(value))

    def __getattr__(self, item):
        try:
            raw_schema = object.__getattribute__(self, '_raw_schema')
            return dict.__getitem__(raw_schema, item)
        except KeyError as ex:
            raise AttributeError(ex)

    def __getitem__(self, item):
        return dict.__getitem__(self._raw_schema, item)


def get(url, auth=None):
    headers = {
        'content-type': 'application/json'
    }
    if auth:
        headers['Authorization'] = '{0} {1}'.format(
            auth['type'], auth['credentials']
        )
    data = requests.get(url, headers=headers).json()
    return Schema(url, data)


def from_header(headers, auth=None):
    if 'content-type' not in headers:
        return None

    full_content_type = 'content-type: {0}'.format(headers['content-type'])
    header, parameters = parse_header(full_content_type)

    if 'profile' not in parameters:
        return None

    schema_url = parameters['profile']
    return get(schema_url, auth)
