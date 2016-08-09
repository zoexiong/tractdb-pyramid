import cornice
import requests

service = cornice.Service(
    name='status',
    path='/',
    description='TractDB Status',
    cors_origins=('*',)
)


@service.get()
def get(request):
    return {
        'status':
            'ready',
        'couchdb':
            requests.get(
                request.registry.settings.tractdb_couchdb
            ).json()
    }
