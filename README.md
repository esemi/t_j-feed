Таблица рейтинга пользователей [Т_Ж](https://journal.tinkoff.ru/)
---

[![build](https://github.com/esemi/t_j-feed/actions/workflows/deployment.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/deployment.yml)
[![wemake-python-styleguide](https://github.com/esemi/t_j-feed/actions/workflows/linters.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/linters.yml)
[![pytest](https://github.com/esemi/t_j-feed/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/tests.yml)

## Usage
[check top users](http://tj.esemi.ru/?l=100)


## Project local running

### install

```bash
$ git clone PATH

$ cd t_j_feed
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
```

### run tests
```bash
$ pytest --cov=t_j_feed tests
$ mypy --ignore-missing-imports t_j_feed/
$ flake8 t_j_feed
```

### run webapp
```bash
$ uvicorn t_j_feed.app:webapp
```
