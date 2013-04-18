import json
import requests
from uritemplate import expand


class RequestMethod(object):

    def __init__(self, rel, method, href, auth):
        self.rel = rel
        self.method = method
        self.href = href
        self.auth = auth

    def _make_get_method(self, resource_id=None):
        url = self.get_url(resource_id)
        return requests.get(url=url, headers=self.get_headers())

    def _make_post_method(self, data):
        url = self.href
        return requests.post(url=url, data=json.dumps(data), headers=self.get_headers())

    def _make_patch_method(self, resource_id, data):
        url = self.get_url(resource_id)
        return requests.patch(url=url, data=json.dumps(data), headers=self.get_headers())

    def _make_put_method(self, resource_id, data):
        url = self.get_url(resource_id)
        return requests.put(url=url, data=json.dumps(data), headers=self.get_headers())

    def _make_delete_method(self, resource_id):
        url = self.get_url(resource_id)
        return requests.delete(url=url, headers=self.get_headers())

    def get_headers(self):
        header = {
            'content-type': 'application/json'
        }
        if self.auth:
            header['Authorization'] = '{0} {1}'.format(self.auth['type'], self.auth['credentials'])

        return header

    @classmethod
    def check_valid_response(cls, response):
        return response.status_code == 200 and 'application/json' in response.headers['content-type']

    @property
    def process(self):
        request_type_by_method = {
            'GET': self._make_get_method,
            'POST': self._make_post_method,
            'PATCH': self._make_patch_method,
            'PUT': self._make_put_method,
            'DELETE': self._make_delete_method
        }
        return request_type_by_method[self.method]

    def get_url(self, resource_id):
        return expand(self.href, {'resource_id': resource_id})