# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

try:
    from unittest import mock
    tests_require = None

except ImportError:
    tests_require = ['mock>=0.8.0']


setup(
    name="crowdflower",
    version="0.0",
    author=u"Ilja Everilä",
    author_email="ilja.everila@liilak.com",
    maintainer=u"Ilja Everilä",
    maintainer_email="ilja.everila@liilak.com",
    description="Unofficial CrowdFlower API client for Python.",
    packages=find_packages(),
    install_requires=[
        'six',
        'requests'
    ],
    tests_require=tests_require,
    include_package_data=True,
    platforms='any',
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Framework :: Setuptools Plugin",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
