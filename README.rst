pluct
=====

.. image:: https://travis-ci.org/globocom/pluct.svg
    :target: https://travis-ci.org/globocom/pluct
    :alt: Travis CI Build Status

A JSON Hyper Schema client that allows hypermedia navigation and
resource validation.

Basic Usage
-----------

.. code:: python

    import pluct

    # Load a resource
    item = pluct.resource('http://myapi.com/api/item', timeout=2)  # Works with connect timeout

    # Verifying if the resource is valid for the current schema
    item.is_valid()

    # Use the resource as a dictionary
    first_title = item['subitems'][0]['title']

    # Accessing the item schema
    item.schema['properties']['title']

    # Loading a related resource
    category = item.rel('category')

    # With additional parameters
    category = item.rel('category', timeout=(1, 2))  # You can choose from request parameters: http://docs.python-requests.org/en/latest/api/#requests.Session.request

Authentication / Custom HTTP Client
-----------------------------------

``Pluct`` uses the `Session <http://docs.python-requests.org/en/latest/api/#request-sessions>`_
object from the `requests <http://docs.python-requests.org/en/latest/>`_ package as a HTTP client.

Any other client with the same interface can be used.

Here is an example using `alf <https://github.com/globocom/alf>`_, an OAuth 2 client:

.. code:: python

    from pluct import Pluct
    from alf.client import Client

    alf = Client(
        token_endpoint='http://myapi.com/token',
        client_id='client-id',
        client_secret='secret')

    # Create a pluct session using the client
    pluct = Pluct(client=alf)
    item = pluct.resource('http://myapi.com/api/item')

All subsequent requests for schemas or resources in this session will
use the same client.

Parameters and URI expansion
----------------------------

`URI Templates <http://tools.ietf.org/html/rfc6570>`_ are supported when following resource links.

The context for URL expansion will be a merge of the resource ``data``
attribute and the ``params`` parameter passed to the resource’s ``rel``
method.

Any variable not consumed by the URL Template will be used on the query
string for the request.

Better explained in an example. Consider the following resource and
schema snippets:

.. code:: json

    {
        "type": "article"
    }

.. code:: json

    {
        "...": "...",
        "links": [
            {
                "rel": "search",
                "href": "/api/search/{type}"
            }
        ]
    }

The next example will resolve the ``href`` from the ``search`` link to
``/api/search/article?q=foo`` and will load articles containing the text
“foo”:

.. code:: python

    import pluct

    # Load a resource
    item = pluct.resource('http://myapi.com/api/item')

    articles = item.rel('search', params={'q': 'foo'})

To search for galleries is just a matter of passing a different ``type``
in the ``params`` argument, as follows:

.. code:: python

    galleries = item.rel('search', params={'type': 'gallery', 'q': 'foo'})

To send your own body data you can send the object as data. This will follow
your method (PUT, POST, GET or DELETE) with all data from object:

.. code:: python

    galleries = item.rel('create', data=item)


Schema loading
--------------

When a resource is loaded, a lazy-schema schema will be created and its
data will only be loaded when accessed.

``Pluct`` looks for a schema URL on the ``profile`` parameter of the
``Content-type`` header:

.. code:: python

    Content-Type: application/json; profile="http://myapi.com/api/schema"

References ($ref)
-----------------

`JSON Pointers <https://tools.ietf.org/html/rfc6901>`_ on schemas are
also supported.

Pointers are identified by a dictionary with a ``$ref`` key pointing to an
external URL or a local pointer.

Considering the following definitions on the ``/api/definitions`` url:

.. code:: json

    {
        "address": {
            "type": "object",
            "properties": {
                "line1": {"type": "string"},
                "line2": {"type": "string"},
                "zipcode": {"type": "integer"},
            }
        }
    }

And this schema on ``/api/schema`` that uses the above definitions:

.. code:: json

    {
        "properties": {
            "shippingAddress": {"$ref": "http://myapi.com/api/definitions#/address"},
            "billingAddress": {"$ref": "http://myapi.com/api/definitions#/address"},
        }
    }

The ``billingAddress`` can be accessed as follows:

.. code:: python

    import pluct
    schema = pluct.schema('http://myapi.com/api/schema')

    schema['properties']['billingAddress']['zipcode'] == {"type": "integer"}

Contributing
------------

Fork the repository on Github:
https://github.com/globocom/pluct

Create a virtualenv and install the dependencies:

.. code:: bash

    make setup

Tests are on the `pluct/tests` directory, run the test suite with:

.. code:: bash

    make test

