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
    config.include('cornice')
    config.scan('tractdb_pyramid.views')

    # Make the app
    app = config.make_wsgi_app()

    return app
