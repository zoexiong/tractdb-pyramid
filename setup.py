import setuptools

VERSION='0.1.1'

setuptools.setup(
    name='tractdb-pyramid',
    version=VERSION,
    description='TractDB Pyramid',
    url='https://tractdb.org',
    packages=['tractdb_pyramid'],
    install_requires=[
    ],
    entry_points="""\
        [paste.app_factory]
        main=tractdb_pyramid:main
        """
    ,
    zip_safe=False,
)
