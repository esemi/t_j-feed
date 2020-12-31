# tj-feed
Лента комментов на Т_Ж
---

Для тех, кому надоело искать новые комменты в старых статьях journal.tinkoff.ru (: 

## Usage
[read last comments online](http://tj.esemi.ru)


### Local run

```bash
$ python3.8 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
$ pytest --cov=tj_feed tests
$ flake8 tj_feed
$ uvicorn tj_feed.app:webapp
```