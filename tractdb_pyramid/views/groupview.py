import cornice
import tractdb.server.groups

service_group = cornice.Service(
    name='group',
    path='/group/{id_group}',
    description='TractDB group',
    cors_origins=('*',),
    cors_credentials=True
)

service_group_collection = cornice.Service(
    name='groups',
    path='/groups',
    description='TractDB Group Collection',
    cors_origins=('*',),
    cors_credentials=True
)


def _get_admin(request):
    # Create our admin object
    admin = tractdb.server.groups.GroupsAdmin(
        couchdb_url=request.registry.settings.tractdb_couchdb,
        couchdb_admin=request.registry.settings.tractdb_couchdb_secrets['admin']['user'],
        couchdb_admin_password=request.registry.settings.tractdb_couchdb_secrets['admin']['password']
    )

    return admin


@service_group.delete()
def delete(request):
    """ Delete an group.
    """

    # Our group parameter
    group = request.matchdict['id_group']

    # Our admin object
    admin = _get_admin(request)

    # Check if the group exists
    if group not in admin.list_groups():
        request.response.status_int = 404
        return

    # Delete the group
    admin.delete_group(group)

    # Return appropriately
    request.response.status_int = 200


@service_group_collection.get()
def collection_get(request):
    """ Get a list of groups.
    """
    # Get the groups
    admin = _get_admin(request)
    list_groups = admin.list_groups()

    # Return appropriately
    request.response.status_int = 200
    return {
        'groups':
            list_groups
    }


@service_group_collection.post()
def collection_post(request):
    """ Create an group.
    """

    # Our JSON parameter, this could be validated
    json = request.json_body
    group_name = json['name']
    group_admin=json['admin']

    # Our admin object
    admin = _get_admin(request)

    # Check if the group exists
    if group in admin.list_groups():
        request.response.status_int = 409
        return

    # Create the group
    admin.create_group(group_name, group_admin)

    # Return appropriately
    request.response.status_int = 201
