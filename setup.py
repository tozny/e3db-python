from setuptools import setup, find_packages
setup(
  name="e3db",
  version="1.0.0",
  packages=find_packages(),
  install_requires="""
PyNaCl >= 1.1, < 2
requests >= 2.18, < 3
""",
  url = "https://github.com/tozny/e3db-python",
  description  = open("README.md").read(),
  author = "Tozny, LLC",
  author_email = "info@tozny.com",
  license = open("LICENSE.md").read()
)
