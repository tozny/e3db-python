# Publishing

## Pre-requisites

[Register an account with PyPi](https://pypi.org/account/register/) (please enable MFA for your account)

Create a [PyPi API token](https://pypi.org/help/#apitoken)

Install twine 

```
pip3 install twine
```

## Releasing a new version

Checkout branch

Write code, tests, and documentation

Submit code for review

Once code has been approved, merge branch

Checkout master branch

Update [setup.py](./setup.py) with the new version (following  [semvar](https://semver.org))

Create release artificats

```
python3 setup.py sdist bdist_wheel
```

Upload to pypi

```
twine upload dist/*
```

Verify you can download the newly published version

```
pip3 install e3db==X.Y.Z
```
