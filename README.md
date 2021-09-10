[Таблица](http://tj.esemi.ru/?l=100) рейтинга пользователей [Т_Ж](https://journal.tinkoff.ru/)
---

[![pytest](https://github.com/esemi/t_j-feed/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/tests.yml)
[![deploy](https://github.com/esemi/t_j-feed/actions/workflows/deployment.yml/badge.svg?branch=master)](https://github.com/esemi/t_j-feed/actions/workflows/deployment.yml)

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
$ pytest --cov=t_j_feed tests
$ mypy --ignore-missing-imports t_j_feed/
$ flake8 t_j_feed
```

### run webapp
```bash
$ uvicorn t_j_feed.app:webapp
```
