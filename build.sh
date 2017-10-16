#! /bin/sh

docker build -t e3db-python:debian . -f Dockerfile.debian
docker build -t e3db-python:alpine . -f Dockerfile.alpine
