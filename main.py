#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys
sys.path.insert(0, 'libs')
from conf import *
import webapp2
import discover
import news



class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

homeapp = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)


class MakeRecord(webapp2.RequestHandler):
    def get(self):
        discover.discover_projects()
        discover.renew_records()
        self.response.write('The database was successfully updated')

recapp = webapp2.WSGIApplication([
    ('/makerecord', MakeRecord)
], debug=True)

class GatherNews(webapp2.RequestHandler):
    def get(self):
        news.news_gather()
        self.response.write('The news were successfully gathered at ' + news.show_time())

newsapp = webapp2.WSGIApplication([
    ('/news', GatherNews)
], debug=True)