import pyramid.config
import pyramid.response
import pyramid.view
import yaml


def main(global_config, **settings):
    # Parse our couchdb secrets
    with open(settings['tractdb_couchdb_secrets']) as f:
        config = yaml.safe_load(f)
    settings['tractdb_couchdb_secrets'] = config

    # Configure our pyramid app
    config = pyramid.config.Configurator(settings=settings)
    config.scan('tractdb_pyramid.views')

    config.add_route('root', '/')

    config.add_route('accounts', '/accounts')
    config.add_route('account', '/accounts/{account}')

    config.add_route('couch', '/couch{request:.*}')

    app = config.make_wsgi_app()

    return app
