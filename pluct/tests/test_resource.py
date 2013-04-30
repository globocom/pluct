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
        }
        self.schema = schema.Schema(
            url="url.com",
            required="platform",
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
        auth = {"type": "t", "credentials": "c"}
        self.result = resource.get(url=self.url, auth=auth)
        schema_get.assert_called_with("url.com", auth)

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
        self.assertFalse(self.result.is_valid())

    @patch("pluct.resource.schema_from_header")
    @patch("requests.get")
    def test_is_valid_invalid(self, get, from_header):
        s = schema.Schema(
            title="title",
            url="url.com",
            required=['platform', 'name'],
            properties={
                u'ip': {u'type': u'string'},
                u'cname': {u'type': u'string'},
                u'name': {u'type': u'string'},
                u'platform': {u'type': u'string'}
            }
        )
        from_header.return_value = s
        data = {
            u'name': u'repos',
        }
        mock = Mock(headers={})
        mock.json.return_value = data
        get.return_value = mock
        result = resource.get(url="appurl.com", auth=None)
        self.assertFalse(result.is_valid())

    @patch("pluct.resource.schema_from_header")
    @patch("requests.get")
    def test_is_valid(self, get, from_header):
        s = schema.Schema(
            title="title",
            url="url.com",
            required=['platform', 'name'],
            properties={
                u'ip': {u'type': u'string'},
                u'cname': {u'type': u'string'},
                u'name': {u'type': u'string'},
                u'platform': {u'type': u'string'}
            }
        )
        from_header.return_value = s
        data = {
            u'name': u'repos',
            u'platform': u'python',
        }
        mock = Mock(headers={})
        mock.json.return_value = data
        get.return_value = mock
        result = resource.get(url="appurl.com", auth=None)
        self.assertTrue(result.is_valid())

    @patch("requests.get")
    def test_method_with_custom_schema(self, get):
        s = schema.Schema(
            title="title",
            url="url.com",
            properties={
                u'name': {u'type': u'string'},
            },
            links=[{
                "href": "http://54.243.182.138:8080/apps/{name}/log",
                "method": "GET",
                "rel": "log",
                "schema": {
                    "required": ["lines"],
                    "properties": {
                        "lines": {"type": "number"},
                        "source": {"type": "string"},
                    }
                }
            }]
        )
        data = {
            u'name': u'repos',
        }
        app = resource.Resource(url="appurl.com", data=data, schema=s)
        app.log(lines=10)
        url = 'http://54.243.182.138:8080/apps/repos/log?lines=10'
        get.assert_called_with(url=url,
                               headers={'content-type': 'application/json'})
        app.log(lines=10, source="app")
        qs = parse_qs(urlparse(get.call_args[1]['url']).query)
        expected = {'source': ['app'], 'lines': ['10']}
        self.assertDictEqual(expected, qs)
