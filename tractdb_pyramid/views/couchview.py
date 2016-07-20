import pyramid.config
import pyramid.response
import pyramid.view
import requests


@pyramid.view.view_defaults(route_name='couch', renderer='json')
class CouchView:
    def __init__(self, request):
        self.request = request

    @pyramid.view.view_config(request_method='GET')
    def get(self):
        query = 'http://tractdbcouch:5984{}'.format(self.request.matchdict['request'])

        return requests.get(
            query
        ).json()
