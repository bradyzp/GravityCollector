# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requires = [
    'Flask==1.0.2',
    'Flask-CORS==3.0.7',
    'Flask-SQLAlchemy==2.3.2',
    'psycopg2==2.7.6.1'
]

setup(
    name='GravityRepo',
    version='0.1.0alpha-4',
    packages=find_packages(),
    package_data={
        '': ['uwsgi.ini', 'wsgi.py', 'gravityrepo.service']
    },
    include_package_data=True,
    install_requires=requires,
    python_requires='>=3.6.*',
    description='',
    author='Zachery Brady',
    author_email='bradyzp@dynamicgravitysystems.com',
    url='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ]
)
