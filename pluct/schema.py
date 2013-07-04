from pluct.request import Request


class Schema(object):
    def __init__(self, url, type=None, title=None, required=None,
                 properties=None, links=None):
        self.url = url
        self.type = type
        if required:
            self.required = required
        self.title = title
        if properties:
            self.properties = properties
        if links:
            self.links = links


def get(url, auth=None):
    data = Request("GET", url, auth).process().json()
    return Schema(
        url=url,
        type=data.get("type"),
        required=data.get("required"),
        title=data.get("title"),
        properties=data.get("properties"),
        links=data.get("links")
    )
