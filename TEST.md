# Documentation

## Build HTML documentation

The following will run on OSX, Linux, and Windows. There is a Unix style `Makefile`, as well as `make.bat` for Windows users.
```
sphinx-apidoc -f -o docs/source e3db
make html
```

# Tests

## Install dependencies
Tests for the e3db-python SDK use pytest. This can be installed by running the following:
```bash
pip install pytest pytest-cov
```

## Run tests and generate a verbose report output

```bash
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
docker run -it --rm \
  -v "$HOME"/.tozny/:/root/.tozny/ \
  -v "$PWD":/src -w /src \
  e3db-python:alpine sh
```
