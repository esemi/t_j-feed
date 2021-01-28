# tj-feed
Лента комментов на Т_Ж
---

Для тех, кому надоело искать новые комменты в старых статьях journal.tinkoff.ru (: 

## Usage
[read last comments online](http://tj.esemi.ru?l=100)

[check top users](http://tj.esemi.ru/top?l=100)


### Local run

```bash
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
$ pytest --cov=tj_feed tests
$ flake8 tj_feed
$ uvicorn tj_feed.app:webapp
```