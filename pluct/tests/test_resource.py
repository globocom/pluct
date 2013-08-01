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

    @patch("requests.get")
    def test_methods(self, get):
        self.assertTrue(hasattr(self.result, "log"))
        self.assertTrue(hasattr(self.result, "env"))
        self.result.log()
        get.assert_called_with(url='/apps/repos/log',
                               headers={'content-type': 'application/json',
                                        'Authorization': 't c'})

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

    @patch("requests.get")
    def test_extra_parameters_querystring(self, get):
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
            headers={'content-type': 'application/json'}
        )

        app.log(lines=10, source="app")
        qs = parse_qs(urlparse(get.call_args[1]['url']).query)
        expected = {'source': ['app'], 'lines': ['10']}
        self.assertEqual(qs, expected)

    @patch("requests.get")
    def test_extra_parameters_uri(self, get):
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
            headers={'content-type': 'application/json'}
        )

    @patch("requests.get")
    def test_extra_parameters_uri_name_bug(self, get):
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
            headers={'content-type': 'application/json'}
        )

    @patch("requests.get")
    def test_schema_with_property_type_array(self, get):
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
                               headers={'content-type': 'application/json'})


class FromResponseTestCase(TestCase):

    def test_should_return_resource_from_response(self):
        response = Response()
        response.url = 'http://example.com'

        returned_resource = resource.from_response(response)

        self.assertEqual(returned_resource.url, 'http://example.com')
