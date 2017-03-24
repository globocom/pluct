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
        'links': [
            {
                'href': 'http://my-awesome-api.com/g1/' +
                        'airports/{resource_id}',
                'rel': 'item'
            },
            {
                'href': 'http://my-awesome-api.com/g1/' +
                        'airports/{resource_id}',
                'method': 'PATCH',
                'rel': 'edit'
            },
            {
                'href': 'http://my-awesome-api.com/g1/' +
                        'airports/{resource_id}',
                'method': 'PUT',
                'rel': 'replace'
            },
            {
                'href': 'http://my-awesome-api.com/g1/' +
                        'airports/{resource_id}',
                'method': 'DELETE',
                'rel': 'delete'
            },
            {
                'href': 'http://my-awesome-api.com/g1/airports',
                'rel': 'self'
            },
            {
                'href': 'http://my-awesome-api.com/g1/airports',
                'method': 'POST',
                'rel': 'create'
            }
        ],
        'item_count': 2
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
                    'name': "Rio de Janeiro",
                    'resource_id': "rio-de-janeiro"
                },
                {
                    'name': "São Paulo",
                    'resource_id': "sao-paulo"
                },
                {
                    'name': "Recife",
                    'resource_id': "recife"
                },
            ],
        }
    )
