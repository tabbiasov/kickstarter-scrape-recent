from google.appengine.api import rdbms
from peewee import *


class AppEngineDatabase(MySQLDatabase):
    def _connect(self, database, **kwargs):
        if 'instance' not in kwargs:
            raise ImproperlyConfigured('Missing "instance" keyword to connect to database')
        return rdbms.connect(database=database, **kwargs)

db = AppEngineDatabase('kickstarter', host='173.194.82.50', instance='starlit-tine-552:kickscrape', user='root', passwd='4509wqwWWR')


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