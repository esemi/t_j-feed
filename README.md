# tj-feed
Таблица рейтинга пользователей Т_Ж
---

[![build](https://github.com/esemi/tj_feed/actions/workflows/deployment.yml/badge.svg?branch=master)](https://github.com/esemi/tj_feed/actions/workflows/deployment.yml)
[![wemake-python-styleguide](https://github.com/esemi/tj_feed/actions/workflows/linters.yml/badge.svg?branch=master)](https://github.com/esemi/tj_feed/actions/workflows/linters.yml)
[![pytest](https://github.com/esemi/tj_feed/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/esemi/tj_feed/actions/workflows/tests.yml)

## Usage
[check top users](http://tj.esemi.ru/top?l=100)


## Project local running

### install

```bash
$ git clone PATH

$ cd tj_feed
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
```

### run tests
```bash
$ pytest --cov=tj_feed tests
$ mypy --ignore-missing-imports tj_feed/
$ flake8 tj_feed
```

### run webapp
```bash
$ uvicorn tj_feed.app:webapp
```
