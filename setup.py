from setuptools import setup, find_packages
version = "2.1.6"
setup(
  name="e3db",
  description="E3DB provides a familiar JSON-based NoSQL-style API for reading, writing, and querying end-to-end encrypted data in the cloud.",
  long_description_content_type='text/markdown',
  long_description=open("README.md").read(),
  version=version,
  packages=find_packages(),
  install_requires=[
    'PyNaCl >= 1.3.0, < 2',
    'requests >= 2.19.1, < 3',
    'Cryptography >= 2.2',
  ],
  url = "https://github.com/tozny/e3db-python",
  download_url = 'https://github.com/tozny/e3db-python/archive/{0}.tar.gz'.format(version),
  author = "Tozny, LLC",
  author_email = "info@tozny.com",
  license = "TOZNY NON-COMMERCIAL LICENSE",
  keywords = ['e3db', 'encryption', 'encrypted-store', 'tozstore'],
  classifiers = [],
)
