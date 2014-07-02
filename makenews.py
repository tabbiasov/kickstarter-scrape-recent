import sys
sys.path.insert(0, 'libs')
from conf import *
import webapp2
import discover
import news


class MainHandler(webapp2.RequestHandler):

    def get(self):
        news.news_gather()
        self.response.write('The news were successfully gathered at ' + news.show_time())

APP = webapp2.WSGIApplication([
    ('/makenews', MainHandler)
], debug=True)
