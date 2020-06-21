# t_j-feed
RSS поток комментов на Т_Ж
---

Для тех, кому надоело искать новые комменты в старых статьях journal.tinkoff.ru (: 

## Usage
[add atom feed](http://t_j.esemi.ru)


### Local run

```shell
$ virtualenv -p python3.8 venv
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
$ pytest --cov=feed tests.py
$ uvicorn feed:app
```