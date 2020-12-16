# tj-feed
RSS поток комментов на Т_Ж
---

Для тех, кому надоело искать новые комменты в старых статьях journal.tinkoff.ru (: 

## Usage
[add atom feed](http://tj.esemi.ru)


### Local run

```shell
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
$ pytest --cov=feed tests.py
$ uvicorn feed:app
```