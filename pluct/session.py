# -*- coding: utf-8 -*-

from requests import Session as RequestsSession

from pluct.request import from_response
from pluct.resource import Resource


class Session(object):

    def __init__(self, client=None, timeout=None):
        self.timeout = timeout

        if client is None:
            self.client = RequestsSession()
        else:
            self.client = client

    def request(self, method, url, *args, **kwargs):
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)

        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('content-type', 'application/json')

        response = self.client.request(method, url, *args, **kwargs)

        return from_response(
            klass=Resource, response=response)
