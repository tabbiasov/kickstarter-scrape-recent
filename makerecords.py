import sys
sys.path.insert(0, 'libs')
from conf import *
import webapp2
import discover
import news


class MainHandler(webapp2.RequestHandler):

    def get(self):
        discover.discover_projects()
        discover.renew_records()
        self.response.write('The database was successfully updated')

APP = webapp2.WSGIApplication([
    ('/makerecords', MainHandler)
], debug=True)
