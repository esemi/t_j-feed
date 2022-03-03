Рейтинговая [таблица](http://tj.esemi.ru/?l=100) пользователей [Т_Ж](https://journal.tinkoff.ru/)
---

[![pytest](https://github.com/esemi/t_j-feed/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/tests.yml)
[![deploy](https://github.com/esemi/t_j-feed/actions/workflows/deployment.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/deployment.yml)
[![CodeQL](https://github.com/esemi/t_j-feed/actions/workflows/codeql-analysis.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/codeql-analysis.yml)
![image](https://user-images.githubusercontent.com/4115497/132915239-ed7e7fa3-07ff-43b3-a3fe-8d6380a34ae7.png)



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
$ pytest --cov=tj_feed tests
$ mypy --ignore-missing-imports tj_feed/
$ flake8 tj_feed
```

### run webapp
```bash
$ gunicorn -k uvicorn.workers.UvicornH11Worker -w 1 tj_feed.app:webapp
```
