# Python Template

This is a template repository for Python projects at BSGIP. It contains a set if configuration files and a suggested directory layout.

## Standard Python Tools

These are the standard python tools that should be used on any new Python projects.

| Name | Configuration file | Purpose | URL |
| --- | --- | --- | --- |
| flake8 | setup.cfg |  Linter | https://flake8.pycqa.org/en/latest/ |
| black | pyproject.toml | Formatter | https://github.com/psf/black |
| isort | setup.cfg | Formats import statements | https://pypi.org/project/isort/ |
| safety | - | Checks for known security vulnerabilities in imported modules | https://pypi.org/project/safety/ |
| codespell | - | Spellchecker | https://pypi.org/project/codespell/ |
| bandit | bandit.yml | Checks your code for security issues | https://github.com/PyCQA/bandit |
| pytest | pytest.ini | Testing Framework | https://docs.pytest.org/ |

Some tools have a configuration settings. The table above indicates in which configuration file to look for settings for that tool. For example, the flake8 settings can be found in the `[flake8]` section of setup.cfg. Others can be find in pyproject.toml

In order to get all the tools to work well together the chosen line length must be consistent. You will see
a value of 120 appearing in multiple places in `pyproject.toml`, `setup.cfg` and also in the editor settings, for example, settings.json for vscode.

We also recommend using [mypy](http://www.mypy-lang.org/). The `pyproject.toml` contains a default configuration and mypy can be enabled in your editors settings (see below)

## .gitignore

The .gitignore is based off [Github standard python .gitignore](https://github.com/github/gitignore/blob/main/Python.gitignore) with a few extra exclusions for files associated with code editors and operating systems.

## Directory structure

We recommend putting your python app/package code in a `src` directory and putting all tests in a `test` directory. This [article](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure) explains some of the benefits to arrange your repository this way.

If you don't want to use the `src` directory, then you will need to change the following settings:

| Config File | Setting |
| --- | --- |
| `setup.cfg` | `package_dir` setting under `[options] |
| `setup.cfg` | `where` setting under `[options.packages.find]` |

If using `mypy` the following `mypy_path` setting under `[mypy]` will also need updating.

## setup.cfg and setup.py

See the discussion here about the merits of [setup.cfg vs setup.py](https://towardsdatascience.com/setuptools-python-571e7d5500f2).

## Editors

This template repository contains example configuration files for the two most popular code editors at BSGIP: [pycharm](https://www.jetbrains.com/pycharm/) and [vscode](https://code.visualstudio.com/).

### pycharm

### vscode

The file `vscode/settings.json` is an example configuration for vscode. To use these setting copy this file to `.vscode/settings,json`

The main features of this settings file are:
    - Enabling flake8 and disabling pylint
    - Autoformat on save (using the black and isort formatters)

Settings that you may want to change:
- Set the python path to your python in your venv with `python.defaultInterpreterPath`.
- Enable mypy by setting `python.linting.mypyEnabled` to true in settings.json.


