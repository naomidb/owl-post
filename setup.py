from setuptools import setup

setup(
    name='owl-post' ,
    version='1.0.0' ,
    description='Send data back and forth from VIVO' ,
    author='' ,
    author_email= '',
    packages=['owlpost'] ,
    install_requires=['bibtexparser', 'certifi', 'chardet', 'docopt', 'idna', 'Jinja2', 'MarkupSafe', 'PyYAML', 'requests', 'urllib3'] ,
)
