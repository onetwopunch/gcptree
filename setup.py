from setuptools import setup
import re
# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

version = None
with open(path.join(this_directory, 'gcptree/cli.py'), encoding='utf-8') as f:
  for line in f.readlines():
    match = re.search("VERSION = \"(.*?)\"$", line)
    if match:
      version = match[1]
      break

setup(name='gcptree',
      version=version,
      description='List your GCP Org heirachy as a tree in JSON or Text',
      url='http://github.com/onetwopunch/gcptree',
      scripts=['bin/gcptree'],
      author='Ryan Canty',
      author_email='onetwopunch@pm.me',
      license='MIT',
      packages=['gcptree'],
      zip_safe=False,
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
        "deepmerge==0.2.1",
        "google-api-python-client==1.12.8",
        "colorama==0.4.3",
      ])