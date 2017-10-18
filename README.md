# e3db-python
Python client library for E3DB

# Documentation

Generate documentation:
```bash
sphinx-apidoc -f -o docs/source e3db
make html
```

# Running Tests

```bash
# install pytest
pip install pytest-cov

# run the tests and output a verbose output report
pytest --cov-report term-missing --cov -v
```

# Build Docker containers

```bash
docker build -t e3db-python:debian . -f Dockerfile.debian
docker build -t e3db-python:alpine . -f Dockerfile.alpine
```

## Shell into Docker container for testing

This is useful when you want to mount your E3DB configuration files into a
containerized environment that has required software installed. This will also
mount the source code inside the container, so any updates to your local git
checkout will be immediately updated inside the container.

```bash
docker run -it --rm -v "$HOME"/.tozny/:/root/.tozny/ -v "$PWD":/src -w /src e3db-python:alpine sh
```
