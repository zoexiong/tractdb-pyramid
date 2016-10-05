import couchdb
import re
import urllib.parse

#roles.py

class GroupsAdmin(object):
    """ Add TractDB groups.
    """

    def __init__(self, couchdb_url, couchdb_admin, couchdb_admin_password):
        """ Create an admin object.
        """
        self._couchdb_url = couchdb_url
        self._couchdb_admin = couchdb_admin
        self._couchdb_admin_password = couchdb_admin_password

    def create_group(self, group_name, group_admin):
        """ Create an group.
        """
        server = self._couchdb_server

        # Our databases are defined by the group name plus the suffix '_tractdb'
        dbname = '{:s}_tractdb'.format(group_name)

        # Directly manipulate groups database, since it's not meaningfully wrapped
        database_groups = server['_groups']
        docid_group = 'org.couchdb.group:{:s}'.format(group_name)

        # Confirm the database does not exist
        if dbname in server:
            raise Exception('Database "{:s}" already exists.'.format(dbname))

        # Confirm the group does not exist
        if docid_group in database_groups:
            raise Exception('Group "{:s}" already exists.'.format(group_name))

        # Create the group
        doc_created_group = {
            '_id': docid_group,
            'type': 'group',
            'name': group_name,
            'admin': group_admin,
            'roles': [],
        }
        database_groups.save(doc_created_group)

        # Create the database
        database_created = server.create(dbname)

        # Give the group access to the database
        security_doc = database_created.security
        security_members = security_doc.get('members', {})
        security_members_names = security_members.get('names', [])
        if group_name not in security_members_names:
            security_members_names.append(group_name)
            security_members_names.sort()
            security_members['names'] = security_members_names
            security_doc['members'] = security_members
            database_created.security = security_doc

    def delete_group(self, group_name):
        """ Delete a group.
        """
        server = self._couchdb_server

        # Our databases are defined by the group name plus the suffix '_tractdb'
        dbname = '{:s}_tractdb'.format(group_name)

        # Directly manipulate groups database, since it's not meaningfully wrapped
        database_groups = server['_groups']
        docid_group = 'org.couchdb.group:{:s}'.format(group_name)

        # Confirm the database exists
        if dbname not in server:
            raise Exception('Database "{:s}" does not exist.'.format(dbname))

        # Confirm the group exists
        if docid_group not in database_groups:
            raise Exception('Group "{:s}" does not exist.'.format(group_name))

        # Delete them
        server.delete(dbname)
        doc_group = database_groups[docid_group]
        database_groups.delete(doc_group)

    def list_groups(self):
        """ List our groups.
        """
        couchdb_groups = self._couchdb_groups
        couchdb_databases = self._couchdb_databases

        # Keep only groups which have a corresponding database
        groups = []
        for group_current in couchdb_groups:
            # Our databases are defined by the group name plus the suffix '_tractdb'
            dbname = '{:s}_tractdb'.format(group_current)

            if dbname in couchdb_databases:
                groups.append(group_current)

        return groups


    def _format_server_url(self):
        """ Format the base URL we use for connecting to the server.
        """
        return '{}://{:s}:{:s}@{:s}'.format(
            urllib.parse.urlparse(self._couchdb_url).scheme,
            self._couchdb_admin,
            self._couchdb_admin_password,
            self._couchdb_url[
                len(urllib.parse.urlparse(self._couchdb_url).scheme) + len('://')
                :
            ]
        )

    @property
    def _couchdb_databases(self):
        """ List what CouchDB databases exist.
        """
        server = self._couchdb_server

        # Our databases are defined by the user name plus the suffix '_tractdb'
        pattern = re.compile('.*_tractdb')
        dbnames = [dbname for dbname in server if pattern.match(dbname)]

        return dbnames

    @property
    def _couchdb_groups(self):
        """ List what CouchDB groups exist.
        """
        server = self._couchdb_server

        # Directly manipulate users database, since it's not meaningfully wrapped
        database_groups = server['_groups']

        # This is our docid pattern
        pattern = re.compile('org\.couchdb\.group:(.*)')

        # Keep only the users that match our pattern, extracting the user
        groups = []
        for docid in database_groups:
            match = pattern.match(docid)
            if match:
                account_group = match.group(1)
                groups.append(account_group)

        return groups

    @property
    def _couchdb_server(self):
        return couchdb.Server(self._format_server_url())
