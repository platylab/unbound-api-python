# Unbound API

## Install and start

```bash
poetry build
pipx install dist/unboundapi-*.whl
unbound-api
```

## Dev

* Needed tooling
  * poetry
  * pre-commit
  * mise

* Installing dependancies

```bash
make install
```

* Adding dependancies

```bash
poetry add <dependancy>
```

* Update dependancies

```bash
make update
```

* Testing

```bash
make check
make test
```

* Use venv to run commands

```bash
poetry shell
```
