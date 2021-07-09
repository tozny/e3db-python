FROM python:3.9-alpine

RUN apk add --no-cache gcc cargo musl-dev libffi-dev make cmake openssl-dev
RUN mkdir -p /src
WORKDIR /src/

RUN pip install --upgrade pip
RUN pip install --no-use-pep517 PyNaCl
RUN pip install -U pytest pytest-cov sphinx flake8

COPY e3db/ /src/e3db/
COPY ["README.md", "LICENSE.md", "setup.py", "/src/"]

RUN python setup.py bdist_wheel && \
  pip install --find-links=./dist/ e3db

COPY integration.py /src/integration.py

ENTRYPOINT ["/src/integration.py"]
