# -*- coding: utf-8 -*-

from pluct import schema


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
