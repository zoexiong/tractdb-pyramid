import pyramid.config
import pyramid.response
import pyramid.view


@pyramid.view.view_defaults(route_name='root', renderer='json')
class RootView:
    def __init__(self, request):
        self.request = request

    @pyramid.view.view_config(request_method='GET')
    def get(self):
        return {
            'tractdb_pyramid': 'version_placeholder',
            'settings': self.request.registry.settings
        }
