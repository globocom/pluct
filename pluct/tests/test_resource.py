# -*- coding: utf-8 -*-


from requests import Response

from unittest import TestCase
from mock import patch, Mock
from urlparse import urlparse, parse_qs

from pluct import resource, schema


class ResourceTestCase(TestCase):

    @patch("pluct.schema.get")
    @patch("requests.get")
    def setUp(self, get, schema_get):
        self.data = {
            "name": "repos",
            "platform": "js",
        }
        self.schema = schema.Schema(
            url="url.com",
            type="object",
            required=["platform"],
            title="some title",
            properties={
                u'name': {u'type': u'string'},
                u'platform': {u'type': u'string'}
            },
            links=[
                {
                    "href": "/apps/{name}/log",
                    "method": "GET",
                    "rel": "log"
                },
                {
                    "href": "/apps/{name}/env",
                    "method": "GET",
                    "rel": "env"
                }
            ]
        )
        schema_get.return_value = self.schema
        self.headers = {
            'content-type': 'application/json; profile=url.com'
        }
        mock = Mock(headers=self.headers)
        mock.json.return_value = self.data
        get.return_value = mock
        self.url = "http://app.com/content"
        self.auth = {"type": "t", "credentials": "c"}
        self.result = resource.get(url=self.url, auth=self.auth)
        schema_get.assert_called_with("url.com", self.auth)

    def test_get_should_returns_a_resource(self):
        self.assertIsInstance(self.result, resource.Resource)

    def test_data(self):
        self.assertEqual(self.data, self.result.data)

    def test_schema(self):
        self.assertEqual(self.schema.url, self.result.schema.url)

    @patch('pluct.resource.from_response')
    @patch("requests.get")
    def test_methods(self, get, resource_from_response):
        self.assertTrue(hasattr(self.result, "log"))
        self.assertTrue(hasattr(self.result, "env"))
        self.result.log()
        get.assert_called_with(url='/apps/repos/log',
                               headers={'content-type': 'application/json',
                                        'Authorization': 't c'},
                               timeout=30)

    def test_is_valid_schema_error(self):
        old = self.result.schema.required
        self.result.schema.required = "ble"
        self.assertFalse(self.result.is_valid())
        self.result.schema.required = old

    @patch("pluct.schema.from_header")
    @patch("requests.get")
    def test_is_valid_invalid(self, get, from_header):
        from_header.return_value = self.schema
        data = {
            u'doestnotexists': u'repos',
        }
        mock = Mock(headers={})
        mock.json.return_value = data
        get.return_value = mock
        result = resource.get(url="appurl.com", auth=None)
        self.assertFalse(result.is_valid())

    def test_is_valid(self):
        self.assertTrue(self.result.is_valid())

    @patch('pluct.resource.from_response')
    @patch("requests.get")
    def test_extra_parameters_querystring(self, get, resource_from_response):
        data = {
            u'name': u'repos',
            u'platform': u'repos',
        }
        app = resource.Resource(url="appurl.com", data=data,
                                schema=self.schema)

        app.log(lines=10)
        url = '/apps/repos/log?lines=10'
        get.assert_called_with(
            url=url,
            headers={'content-type': 'application/json'},
            timeout=30
        )

        app.log(lines=10, source="app")
        qs = parse_qs(urlparse(get.call_args[1]['url']).query)
        expected = {'source': ['app'], 'lines': ['10']}
        self.assertEqual(qs, expected)

    @patch('pluct.resource.from_response')
    @patch("requests.get")
    def test_extra_parameters_uri(self, get, resource_from_response):
        data = {
            u'name': u'repos',
            u'platform': u'repos',
        }
        self.schema.links[0]['href'] = '/apps/{name}/log/{lines}'
        app = resource.Resource(url="appurl.com", data=data,
                                schema=self.schema)

        app.log(lines=10, source="app")
        url = '/apps/repos/log/10?source=app'
        get.assert_called_with(
            url=url,
            headers={'content-type': 'application/json'},
            timeout=30
        )

    @patch('pluct.resource.from_response')
    @patch("requests.get")
    def test_extra_parameters_timeout_uri(self, get, resource_from_response):
        data = {
            u'name': u'repos',
            u'platform': u'repos',
        }
        self.schema.links[0]['href'] = '/apps/{name}/log/{lines}'
        app = resource.Resource(url="appurl.com", data=data,
                                schema=self.schema, timeout=10)

        app.log(lines=10, source="app")
        url = '/apps/repos/log/10?source=app'
        get.assert_called_with(
            url=url,
            headers={'content-type': 'application/json'},
            timeout=10
        )

    @patch('pluct.resource.from_response')
    @patch("requests.get")
    def test_extra_parameters_uri_name_bug(self, get, resource_from_response):
        # regression for #12.
        data = {'platform': 'xpto'}
        link = {
            "href": "http://example.org/{context_name}",
            "method": "GET",
            "rel": "example"
        }
        self.schema.links.append(link)
        app = resource.Resource(url="appurl.com", data=data,
                                schema=self.schema)

        app.example(context_name='context', name='value1')
        url = 'http://example.org/context?name=value1'
        get.assert_called_with(
            url=url,
            headers={'content-type': 'application/json'},
            timeout=30
        )

    @patch('pluct.resource.from_response')
    @patch("requests.get")
    def test_schema_with_property_type_array(self, get, from_response):
        s = schema.Schema(
            title="title",
            type="object",
            url="url.com",
            properties={
                u'items': {
                    u'type': u'array',
                    u'items': {
                        'title': 'Foo',
                        'type': 'object',
                        'properties': {
                            'id': {
                                'type': 'integer'
                            }
                        },
                        'links': [{
                            "href": "http://localhost/foos/{id}/",
                            "method": "GET",
                            "rel": "item",
                        }]
                    }
                },
            },
        )
        data = {
            'items': [
                {'id': 1},
                {'id': 2}
            ]
        }
        app = resource.Resource(url="appurl.com", data=data, schema=s)
        app.data['items'][0].item()
        url = 'http://localhost/foos/1/'
        get.assert_called_with(url=url,
                               headers={'content-type': 'application/json'},
                               timeout=30)


class FromResponseTestCase(TestCase):

    def setUp(self):
        self._response = Response()
        self._response.url = 'http://example.com'
        content_type = 'application/json; profile=http://example.com/schema'
        self._response.headers = {
            'content-type': content_type
        }
        self._auth = {'type': 't', 'credentials': 'c'}

    @patch('pluct.schema.from_header')
    def test_should_return_resource_from_response(self, from_header):
        self._response.json = Mock(return_value={})
        returned_resource = resource.from_response(self._response, self._auth)
        self.assertEqual(returned_resource.url, 'http://example.com')
        self.assertEqual(returned_resource.auth, self._auth)
        self.assertEqual(returned_resource.data, {})

    @patch('pluct.schema.from_header')
    def test_should_return_resource_from_response_with_no_json_data(
            self, from_header):
        self._response.json = Mock(side_effect=ValueError())
        returned_resource = resource.from_response(self._response, self._auth)
        self.assertEqual(returned_resource.url, 'http://example.com')
        self.assertEqual(returned_resource.auth, self._auth)
        self.assertEqual(returned_resource.data, {})

    @patch('pluct.schema.from_header')
    def test_should_obtain_schema_from_header(self, from_header):
        self._response.json = Mock(side_effect=ValueError())
        resource.from_response(self._response, self._auth)
        from_header.assert_called_with(self._response.headers, self._auth)

    def test_resource_with_an_array_without_schema(self):
        data = {
            u'units': [
                {u'name': u'someunit'}
            ],
            u'name': u'registry',
        }
        s = schema.Schema(
            url='url',
            title='app schema',
            type='object',
            required=['name'],
            properties={'name': {'type': 'string'}}
        )
        response = resource.Resource("url", data, s)
        self.assertDictEqual(data, response.data)
