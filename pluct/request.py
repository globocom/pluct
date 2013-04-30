import json
import requests
import urllib


class Request(object):

    def __init__(self, method, href, auth):
        self.method = method
        self.href = href
        self.auth = auth

    def _get(self, **kwargs):
        querystring = urllib.urlencode(kwargs)
        url = self.href
        if querystring:
            url += "?{0}".format(querystring)
        return requests.get(url=url, headers=self.get_headers())

    def _post(self, **kwargs):
        data = kwargs.pop('data')
        return requests.post(url=self.href, data=json.dumps(data),
                             headers=self.get_headers())

    def _patch(self, **kwargs):
        data = kwargs.pop('data')
        return requests.patch(url=self.href, data=json.dumps(data),
                              headers=self.get_headers())

    def _put(self, **kwargs):
        data = kwargs.pop('data')
        return requests.put(url=self.href, data=json.dumps(data),
                            headers=self.get_headers())

    def _delete(self, **kwargs):
        return requests.delete(url=self.href, headers=self.get_headers())

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
        request_type_by_method = {
            'GET': self._get,
            'POST': self._post,
            'PATCH': self._patch,
            'PUT': self._put,
            'DELETE': self._delete,
        }
        return request_type_by_method[self.method]
