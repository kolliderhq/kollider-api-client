from setuptools import setup

setup(name='kollider_api_client',
      version='1.0',
      packages=['kollider_api_client'],
      scripts=[],
      install_requires=[
          'requests',
          'websocket-client',
          'future',
          'urllib3',
          'greenlet',
          'idna',
          'charset-normalizer',
          'zope.event',
          'zope.interface',
          'certifi'
      ],
      package_data={},
   )