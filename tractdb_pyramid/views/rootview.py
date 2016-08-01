import cornice
import requests

service = cornice.Service(
    name='root',
    path='/',
    description='TractDB Information',
    cors_origins=('*',)
)


@service.get()
def get(request):
    return {
        'tractdb_pyramid':
            'version_placeholder',
        'tractdb_couchdb':
            requests.get(
                request.registry.settings.tractdb_couchdb
            ).json()
    }
