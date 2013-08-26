#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ujson
import mock


class ServiceSchemaMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = ujson.dumps(
        {
            'items': [
                {
                    'collection_name': "airports",
                    # 'resource_id': "airport",
                },
                {
                    'collection_name': "cities",
                    # 'resource_id': "city",
                }
            ],

            'item_count': 2
        }
    )


class ResourceMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json; profile=http://my-api.com/v1/schema'
    }
    status_code = 200


class ResourceSchemaMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    json = {
        u'links': [
            {
                u'href': 'http://my-awesome-api.com/g1/' +
                         'airports/{resource_id}',
                u'rel': u'item'
            },
            {
                u'href': 'http://my-awesome-api.com/g1/' +
                         'airports/{resource_id}',
                u'method': u'PATCH',
                u'rel': u'edit'
            },
            {
                u'href': 'http://my-awesome-api.com/g1/' +
                         'airports/{resource_id}',
                u'method': u'PUT',
                u'rel': u'replace'
            },
            {
                u'href': 'http://my-awesome-api.com/g1/' +
                         'airports/{resource_id}',
                u'method': u'DELETE',
                u'rel': u'delete'
            },
            {
                u'href': u'http://my-awesome-api.com/g1/airports',
                u'rel': u'self'
            },
            {
                u'href': u'http://my-awesome-api.com/g1/airports',
                u'method': u'POST',
                u'rel': u'create'
            }
        ],
        u'item_count': 2
    }

    @property
    def content(self):
        return ujson.dumps(self.json)


class ResourceItemsMock(mock.MagicMock):
    headers = {
        'content-type': 'application/json'
    }
    status_code = 200
    content = ujson.dumps(
        {
            'items': [
                {
                    u'name': u"Rio de Janeiro",
                    u'resource_id': u"rio-de-janeiro"
                },
                {
                    u'name': u"São Paulo",
                    u'resource_id': u"sao-paulo"
                },
                {
                    u'name': u"Recife",
                    u'resource_id': u"recife"
                },
            ],
        }
    )
