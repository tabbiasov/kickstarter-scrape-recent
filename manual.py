import requests
from peewee import *
import time

db = MySQLDatabase('kickstarter', host='localhost', user='root', passwd='4509wqwWWR')

class Projects(Model):
    id = IntegerField(primary_key=True)
    name = CharField(100)
    goal = IntegerField()
    currency = CharField(30)
    country = CharField(30)
    created_at = IntegerField()
    launched_at = IntegerField()
    deadline = IntegerField()
    parent_category = CharField(30)
    location_woeid = IntegerField()
    creator_id = IntegerField()
    disable_communication = BooleanField()
    currency_trailing_code = BooleanField()

    class Meta:
        database = db


class Snapshots(Model):
    timestamp = IntegerField()
    id = ForeignKeyField(Projects, on_update='CASCADE', on_delete='CASCADE')
    pledged = IntegerField()
    backers_count = IntegerField()
    status = CharField(1)

    class Meta:
        database = db

class News(Model):
    timestamp = IntegerField(primary_key=True)
    google_count = IntegerField()
    twitter_count = IntegerField()

    class Meta:
        database = db


class Sessions(Model):
    session_id = PrimaryKeyField()
    started_at = IntegerField()
    ended_at = IntegerField()
    pages_screened = IntegerField()
    status = CharField(10)

    class Meta:
        database = db


class Snaps(Model):
    session = ForeignKeyField(Sessions, on_update='CASCADE', on_delete='CASCADE', index=True)
    id = ForeignKeyField(Projects, on_update='CASCADE', on_delete='CASCADE', index=True)
    pledged = IntegerField()
    backers_count = IntegerField()
    status = CharField(1)

    class Meta:
        database = db



def url(p):
    return "https://www.kickstarter.com/discover/recently-launched?page=" + str(p) + "&seed="

hdr = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4",
    "X-Requested-With": "XMLHttpRequest",
}


def restart():
    Projects.delete().where(True).execute()
    i = 0
    data = requests.get(url(1), headers=hdr).json()['projects']
    Projects.create(id=data[i]['id'],
                    name=data[i]['name'],
                    goal=data[i]['goal'],
                    currency=data[i]['currency'],
                    country=data[i]['country'],
                    created_at=data[i]['created_at'],
                    launched_at=data[i]['launched_at'],
                    deadline=data[i]['deadline'],
                    parent_category=data[i]['category'].get('parent_id', data[i]['category'].get('id')),
                    location_woeid=data[i]['location']['id'],
                    creator_id=data[i]['creator']['id'],
                    disable_communication=data[i]['disable_communication'],
                    currency_trailing_code=data[i]['currency_trailing_code'])


def count_records():

    db.connect()

    end_not_reached = True
    p = 1
    delay = 360
    end_id = Projects\
        .select()\
        .where(Projects.deadline >= time.time()-delay)\
        .order_by(Projects.launched_at.asc())\
        .first()\
        .id
    session_buffer = set()

    while end_not_reached:
        i = 0
        data = requests.get(url(p), headers=hdr).json()['projects']
        while end_not_reached & (i < len(data)):
            curr_id = data[i]['id']
            if not(curr_id in session_buffer):
                session_buffer.add(curr_id)
            i += 1
            if curr_id == end_id:
                end_not_reached = False
        p += 1

    print(len(session_buffer))
