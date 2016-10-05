import couchdb
import re
import urllib.parse

#roles.py

class Role(object):
    """ Add TractDB roles.
    """

    def __init__(self, couchdb_url, couchdb_admin, couchdb_admin_password):
        """ Create an admin object.
        """
        self._couchdb_url = couchdb_url
        self._couchdb_admin = couchdb_admin
        self._couchdb_admin_password = couchdb_admin_password

    def create_account(self, role_name, role_admin):
        """ Create an role.
        """
        server = self._couchdb_server

        # Our databases are defined by the role name plus the suffix '_tractdb'
        dbname = '{:s}_tractdb'.format(role_name)

        # Directly manipulate roles database, since it's not meaningfully wrapped
        database_roles = server['_roles']
        docid_role = 'org.couchdb.role:{:s}'.format(role_name)

        # Confirm the database does not exist
        if dbname in server:
            raise Exception('Database "{:s}" already exists.'.format(dbname))

        # Confirm the role does not exist
        if docid_role in database_roles:
            raise Exception('role "{:s}" already exists.'.format(role_name))

        # Create the role
        doc_created_role = {
            '_id': docid_role,
            'type': 'role',
            'name': role_name,
            'admin': role_admin,
            'roles': [],
        }
        database_roles.save(doc_created_role)

        # Create the database
        database_created = server.create(dbname)

        # Give the account access to the database
        security_doc = database_created.security
        security_members = security_doc.get('members', {})
        security_members_names = security_members.get('names', [])
        if role_name not in security_members_names:
            security_members_names.append(role_name)
            security_members_names.sort()
            security_members['names'] = security_members_names
            security_doc['members'] = security_members
            database_created.security = security_doc

    def delete_role(self, role_name):
        """ Delete a role.
        """
        server = self._couchdb_server

        # Our databases are defined by the role name plus the suffix '_tractdb'
        dbname = '{:s}_tractdb'.format(role_name)

        # Directly manipulate roles database, since it's not meaningfully wrapped
        database_roles = server['_roles']
        docid_role = 'org.couchdb.role:{:s}'.format(role_name)

        # Confirm the database exists
        if dbname not in server:
            raise Exception('Database "{:s}" does not exist.'.format(dbname))

        # Confirm the role exists
        if docid_role not in database_roles:
            raise Exception('role "{:s}" does not exist.'.format(role_name))

        # Delete them
        server.delete(dbname)
        doc_role = database_roles[docid_role]
        database_roles.delete(doc_role)

    def list_roles(self):
        """ List our roles.
        """
        couchdb_roles = self._couchdb_roles
        couchdb_databases = self._couchdb_databases

        # Keep only roles which have a corresponding database
        roles = []
        for role_current in couchdb_roles:
            # Our databases are defined by the role name plus the suffix '_tractdb'
            dbname = '{:s}_tractdb'.format(role_current)

            if dbname in couchdb_databases:
                roles.append(role_current)

        return roles

    # def reset_password(self, account, account_password):
    #     """ Reset an account password.
    #     """
    #     server = self._couchdb_server
    #
    #     # Our databases are defined by the user name plus the suffix '_tractdb'
    #     dbname = '{:s}_tractdb'.format(account)
    #
    #     # Directly manipulate users database, since it's not meaningfully wrapped
    #     database_users = server['_users']
    #     docid_user = 'org.couchdb.user:{:s}'.format(account)
    #
    #     # Confirm the database exists
    #     if dbname not in server:
    #         raise Exception('Database "{:s}" does not exist.'.format(dbname))
    #
    #     # Confirm the user exists
    #     if docid_user not in database_users:
    #         raise Exception('User "{:s}" does not exist.'.format(account))
    #
    #     # Get the existing document
    #     doc_user = database_users[docid_user]
    #
    #     # Change the password and put it back
    #     doc_user['password'] = account_password
    #     database_users.update([doc_user])

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
    def _couchdb_roles(self):
        """ List what CouchDB roles exist.
        """
        server = self._couchdb_server

        # Directly manipulate users database, since it's not meaningfully wrapped
        database_roles = server['_roles']

        # This is our docid pattern
        pattern = re.compile('org\.couchdb\.role:(.*)')

        # Keep only the users that match our pattern, extracting the user
        roles = []
        for docid in database_roles:
            match = pattern.match(docid)
            if match:
                account_role = match.role(1)
                roles.append(account_role)

        return roles

    @property
    def _couchdb_server(self):
        return couchdb.Server(self._format_server_url())
