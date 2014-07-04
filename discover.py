#gitHub testing
import time
import logging
import requests
import socket
from requests.adapters import HTTPAdapter
from google.appengine.api import urlfetch
from conf import *

def url(p):
    return "https://www.kickstarter.com/discover/recently-launched?page=" + str(p) + "&seed="

hdr = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip,deflate,sdch",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4",
    "X-Requested-With": "XMLHttpRequest",
}

def discover_projects():

    db.connect()

    new = True
    p = 1
    session_buffer = set()

    s = requests.Session()
    s.mount('https://www.kickstarter.com', HTTPAdapter(max_retries=10))

    while new:
        i = 0
        data = s.get(url(p), headers=hdr).json()['projects']
        while new & (i < len(data)):
            if not(data[i]['id'] in session_buffer):
                session_buffer.add(data[i]['id'])
                try:
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
                                    currency_trailing_code=data[i]['currency_trailing_code'],
                                    link=data[i]['urls']['web']['project'])
                except IntegrityError:
                    new = False
            i += 1
        p += 1

def renew_records():

    db.connect()

    end_not_reached = True
    p = 1
    delay = 2700  # 45 minutes
    session_status = 1

    marker_project = Projects\
        .select()\
        .where(Projects.deadline >= time.time() - delay, Projects.launched_at != 0)\
        .order_by(Projects.launched_at.asc())\
        .first()

    end_id = marker_project.id
     # Take the earliest launched project from those with deadline not more than 45 minutes before
             # and with time launched not 0 as a marker of reached end (end_not_reached=false)
    full_stop_launched_at = marker_project.launched_at

    session_num = Sessions.select().order_by(Sessions.session_id.desc()).first().session_id + 1  # increment session num
    session_started = int(time.time())  # record session started time

    session_buffer = set()  # create an empty session buffer to avoid dealing with project twice during
                            # one session if some structural changes in projects list occur
                            # on the side of kickstarter (adding, removing etc.)

    Sessions.create(session_id=session_num,
                    started_at=session_started,
                    ended_at=0,
                    pages_screened=-1,
                    status=0)  # record initial session params in sessions table

    s = requests.Session()  # create session for fetching url
    s.mount('https://www.kickstarter.com', HTTPAdapter(max_retries=10))  # mount specific adapter to the session
                                                                         # that wou use max_retires=10 for the prefix

    urlfetch.set_default_fetch_deadline(45)  # set 30 secs for default fetch deadline in GAE
    socket.setdefaulttimeout(45)

    try:  # to avoid breaks in execution use exceptions for any errors and record error codes in the end
        while end_not_reached:  # while the marker project is not reached
            i = 0
            data = s.get(url(p), headers=hdr).json()['projects']  # request all info from a page
                                                                  # in JSON and parse it to a dictionary
            while end_not_reached & (i < len(data)):  # check for the page end
                curr_id = data[i]['id']  # remember the current project's ID to avoid quering twice
                if not (data[i]['launched_at'] < full_stop_launched_at):
                    if not(curr_id in session_buffer):  # if this ID was not managed before, deal with it
                                                        # if it was, go ahead
                        session_buffer.add(curr_id)  # if not dealt before add the ID to the session buffer
                        try:  # if the project is not yet in the database (projects. table)
                              # it will not make records for it to keep consistency of snaps table and projects table
                            Snaps.create(session=session_num,
                                         id=curr_id,
                                         pledged=data[i]['pledged'],
                                         backers_count=data[i]['backers_count'],
                                         status=data[i]['state'][0].upper())
                        except Projects.DoesNotExist:
                            logging.warning('Project ' + str(curr_id) + ' is not in the projects list!')
                            # if the project is not yet in the database send warning
                    i += 1
                    if curr_id == end_id:  # check whether marker project is reached, which means the end of list
                        end_not_reached = False
                else:
                    end_not_reached = False
                    session_status = 2
            p += 1
    except Exception, e:  # in case of any exception record its message to include in sessions table
        logging.error('Error with message: ' + str(e))
        session_status = str(e)

    q = Sessions.update(started_at=session_started,
                        ended_at=int(time.time()),
                        pages_screened=p,
                        status=session_status).where(Sessions.session_id == session_num)
                        #  record resulting session params in sessions table (with error code if an error occured)
    q.execute()