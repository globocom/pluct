# -*- coding: utf-8 -*-

import ujson
import urllib

import requests
from uritemplate import expand

from pluct import schema


class Request(object):

    def __init__(self, method, href, resource):
        self.method = method
        self.href = href
        self.resource = resource
        self._request_type_by_method = {
            'GET': self._get,
            'POST': self._post,
            'PATCH': self._patch,
            'PUT': self._put,
            'DELETE': self._delete,
        }

    def _remote(self):
        return requests

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
        return header

    @property
    def process(self):
        return self._request_type_by_method[self.method]


def from_response(klass, response):
    try:
        data = response.json()
    except ValueError:
        data = {}
    return klass(
        url=response.url,
        data=data,
        schema=schema.from_header(response.headers),
        response=response
    )
