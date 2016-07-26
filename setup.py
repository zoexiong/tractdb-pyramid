import setuptools

setuptools.setup(
    name='tractdb-pyramid',
    version='0.1.1',
    description='TractDB Pyramid',
    url='https://tractdb.org',
    packages=['tractdb_pyramid'],
    install_requires=[
        'click==6.6',
        'couchdb==1.0.1',
        'first==2.0.1',
#        'invoke==0.12.2',
        'jinja2==2.8',
        'markupsafe==0.23',
        'nose==1.3.7',
        'pastedeploy==1.5.2',
        'pip-tools==1.6.5',
        'pyramid==1.7',
        'repoze.lru==0.6',
        'requests==2.10.0',
        'six==1.10.0',
        'tractdb==0.1.3',
        'translationstring==1.3',
        'venusian==1.0',
        'waitress==0.9.0',
        'webob==1.6.1',
        'zope.deprecation==4.1.2',
        'zope.interface==4.2.0',

        'pyyaml==3.11'
    ],
    entry_points="""\
        [paste.app_factory]
        main=tractdb_pyramid:main
        """
    ,
    zip_safe=False,
)
