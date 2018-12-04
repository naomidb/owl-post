from setuptools import setup, find_packages

config = {
  'description': 'A collection of queries and tools for interacting with VIVO',
  'author': '',
  'url': '',
  'author_email': '',
  'version': '',
  'install requires': [
      'requests==2.18.4',
      'PyYAML==3.12',
      'Jinja2==2.10'
  ],
  'dependency_links': [],
  'include_package_data': True,
  'packages': find_packages(),
  'scripts': [],
  'entry_points': {
    'console_scripts': [
        'owlpost = owlpost.__main__:cli_run'
    ]
  },
  'name': 'owlpost'
}

setup(**config)