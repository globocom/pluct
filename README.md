pluct
=====

[![Build Status](https://drone.io/github.com/globocom/pluct/status.png)](https://drone.io/github.com/globocom/pluct/latest)
[![Build Status](https://travis-ci.org/globocom/pluct.png?branch=master)](https://travis-ci.org/globocom/pluct)

```python
from pluct import resource
app = resource.get("http://myapi.com/app/myapp")
```

verifying if the resource is valid:
```python
app.is_valid()
```

retrieve the resource data:
```python
app.data
```

retrieve the resource schema:
```python
app.schema
```

Limitations
-----------

*pluct* is an experimental project. its limitations:

* partial support for draft 4.


Tests
-----

The ``tests`` directory contains the standard test stack for pluct.


