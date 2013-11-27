# -*- coding: utf-8 -*-

import ujson
import urllib

import requests
from uritemplate import expand
from alf.client import Client

from pluct import schema


class Credentials(object):

    def __init__(self, token_endpoint, client_id, client_secret):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret


class Request(object):

    def __init__(self, method, href, auth, resource, credentials=None):
        self.method = method
        self.href = href
        self.auth = auth
        self.resource = resource
        self._request_type_by_method = {
            'GET': self._get,
            'POST': self._post,
            'PATCH': self._patch,
            'PUT': self._put,
            'DELETE': self._delete,
        }
        self._credentials = credentials
        if self._credentials:
            if not isinstance(self._credentials, Credentials):
                msg = u"Request was initialized with invalid credentials {0:s}"
                raise TypeError(msg.format(credentials))

            self._client = Client(token_endpoint=credentials.token_endpoint,
                                  client_id=credentials.client_id,
                                  client_secret=credentials.client_secret)

    def _remote(self):
        return self._credentials if self._credentials else requests

    def _get(self, **kwargs):
        data = self.resource.data
        data.update(kwargs)
        url = expand(self.href, data)
        for var in kwargs.keys():
            if "{{{}}}".format(var) in self.href:
                kwargs.pop(var)
        querystring = urllib.urlencode(kwargs)
        if querystring:
            url += "?{0}".format(querystring)

        response = self._remote().get(url=url,
                                      headers=self.get_headers(),
                                      timeout=self.resource.timeout)
        return from_response(self.resource.__class__, response)

    def _post(self, **kwargs):
        self.href = expand(self.href, self.resource.data)
        data = kwargs.pop('data')
        response = self._remote().post(url=self.href,
                                       data=ujson.dumps(data),
                                       headers=self.get_headers(),
                                       timeout=self.resource.timeout)
        return from_response(self.resource.__class__, response)

    def _patch(self, **kwargs):
        self.href = expand(self.href, self.resource.data)
        data = kwargs.pop('data')
        response = self._remote().patch(url=self.href,
                                        data=ujson.dumps(data),
                                        headers=self.get_headers(),
                                        timeout=self.resource.timeout)
        return from_response(self.resource.__class__, response)

    def _put(self, **kwargs):
        self.href = expand(self.href, self.resource.data)
        data = kwargs.pop('data')
        response = self._remote().put(url=self.href,
                                      data=ujson.dumps(data),
                                      headers=self.get_headers(),
                                      timeout=self.resource.timeout)
        return from_response(self.resource.__class__, response)

    def _delete(self, **kwargs):
        self.href = expand(self.href, self.resource.data)
        response = self._remote().delete(url=self.href,
                                         headers=self.get_headers(),
                                         timeout=self.resource.timeout)
        return from_response(self.resource.__class__, response)

    def get_headers(self):
        header = {
            'content-type': 'application/json'
        }
        if self.auth:
            header['Authorization'] = '{0} {1}'.format(
                self.auth['type'], self.auth['credentials'])

        return header

    @property
    def process(self):
        return self._request_type_by_method[self.method]


def from_response(klass, response, auth=None):
    try:
        data = response.json()
    except ValueError:
        data = {}
    return klass(
        url=response.url,
        auth=auth,
        data=data,
        schema=schema.from_header(response.headers, auth),
        response=response
    )
