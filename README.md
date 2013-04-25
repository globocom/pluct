api-manager-client
==================

[![Build Status](https://drone.io/github.com/globocom/pluct/status.png)](https://drone.io/github.com/globocom/pluct/latest)


```python
from apimanagerclient import Service
my_service = Service('http://repos.plataformas.glb.com/g1/')
```

retrieve all items os your resource:
```python
my_service.cities.all()
```

add new item:

```python
my_service.cities.create('name': 'Fortaleza'})
```

delete
```python
ss.cities.delete('RESOURCE_ID_OF_AN_ITEM')
```

Edit
```python
ss.cities.edit('RESOURCE_ID_OF_AN_ITEM', {'name': 'Porto Alegre'})
```

Replace
```python
ss.cities.replace('RESOURCE_ID_OF_AN_ITEM', {'name': 'Porto Alegre'})
```
