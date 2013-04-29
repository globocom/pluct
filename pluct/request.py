import json
import requests
from uritemplate import expand


class Request(object):

    def __init__(self, method, href, auth):
        self.method = method
        self.href = href
        self.auth = auth

    def _get(self, **kwargs):
        url = self.get_url(**kwargs)
        return requests.get(url=url, headers=self.get_headers())

    def _post(self, **kwargs):
        data = kwargs.pop('data')
        url = self.get_url(**kwargs)
        return requests.post(url=url, data=json.dumps(data),
                             headers=self.get_headers())

    def _patch(self, **kwargs):
        data = kwargs.pop('data')
        url = self.get_url(**kwargs)
        return requests.patch(url=url, data=json.dumps(data),
                              headers=self.get_headers())

    def _put(self, **kwargs):
        data = kwargs.pop('data')
        url = self.get_url(**kwargs)
        return requests.put(url=url, data=json.dumps(data),
                            headers=self.get_headers())

    def _delete(self, **kwargs):
        url = self.get_url(**kwargs)
        return requests.delete(url=url, headers=self.get_headers())

    def get_headers(self):
        header = {
            'content-type': 'application/json'
        }
        if self.auth:
            header['Authorization'] = '{0} {1}'.format(
                self.auth['type'], self.auth['credentials'])

        return header

    @classmethod
    def check_valid_response(cls, response):
        return response.status_code == 200 and 'application/json' in response.headers['content-type']

    @property
    def process(self):
        request_type_by_method = {
            'GET': self._get,
            'POST': self._post,
            'PATCH': self._patch,
            'PUT': self._put,
            'DELETE': self._delete,
        }
        return request_type_by_method[self.method]

    def get_url(self, **kwargs):
        return expand(self.href, kwargs)
