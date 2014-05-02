import sys

sys.path.insert(0, 'libs')

import requests
import re
import time
import datetime
from bs4 import BeautifulSoup
from conf import *
from twython import Twython


def twitter_count():

    #Set parameters
    keyword = 'kickstarter'; #The desired keyword(s)
    tweetsXiteration = 100; #Where 100 is the max
    d = datetime.timedelta(days=1)
    today = datetime.date.today()
    yesterday = today - d
    dateFrom = yesterday.strftime("%Y-%m-%d"); #Inclusive (YYYY-MM-DD)
    dateTo = today.strftime("%Y-%m-%d"); #Exclusive (YYYY-MM-DD)
    done = False; #Must be false

    #Setting the OAuth
    Consumer_Key = '0Io4CpjhioOrhvsUV4JFNDhER';
    Consumer_Secret = '0CIK7WinLIys6RqrthW4tZ1naKqT5t0xkEkUD7mgjhkjETxKt2';
    Access_Token = '297465676-tYLgZxyI5tUxkBOZkzu2LR3jNKZXQhLopPpCwmJi';
    Access_Token_Secret = 'lDmvxgN0mpxgXEVjQrqROGPwvv4xvctiyGCNLnhmPOEsY';

    #Connection established with Twitter API v1.1
    twitter = Twython(Consumer_Key, Consumer_Secret, Access_Token, Access_Token_Secret);

    #Twitter is queried
    response = twitter.search(q=keyword, count=tweetsXiteration, since=dateFrom, until=dateTo, result_type='mixed');

    #Results (partial)
    countTweets = len(response['statuses']);

    #If all the tweets have been fetched, then we are done
    if not ('next_results' in response['search_metadata']):
        done = True;

    #If not all the tweets have been fetched, then...
    while (done == False):

        #Parsing information for maxID
        parse1 = response['search_metadata']['next_results'].split("&");
        parse2 = parse1[0].split("?max_id=");
        parse3 = parse2[1];
        maxID = parse3;

        #Twitter is queried (again, this time with the addition of 'max_id')
        response = twitter.search(q=keyword, count=tweetsXiteration, since=dateFrom, until=dateTo, max_id=maxID, include_entities=1, result_type='mixed');

        #Updating the total amount of tweets fetched
        countTweets = countTweets + len(response['statuses']);

        #If all the tweets have been fetched, then we are done
        if not ('next_results' in response['search_metadata']):
            done = True;
    return countTweets


hdr = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip,deflate,sdch",
    "accept-language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4",
    "cache-control": "max-age=0",
    "cookie": "HSID=AE4jRLtX-n1uKsXCQ; SSID=AMKsySyaSTlpGSS_e; APISID=0BqDcA16QJ2vhOkb/AxXv6kBOJiasIFj9Y; SAPISID=FToKktQwx4RNIXiv/AVp74KZ6CSE1G7dal; S=izeitgeist-ad-metrics=_8tj8p_lfX4:photos_html=IA6cQy_314dYWaJVy-vjjg:adwords-usermgmt=AzQw4qopJ9LwhYXYb7OVAQ:awfe=8qgtsXZPZ4eW01-_Q0uKtw:awfe-efe=8qgtsXZPZ4eW01-_Q0uKtw:adwords-campaignmgmt=G2L9saxNUPvNpADmhGVtrA:adwords-common-ui=rFXvX5HqzN5rISQCoPz9AA:adwords-navi=uxnP_XeruEDDs5PBIjxDIA:adwords-dashboard=ApQD7ddyhBvBG2OE1rBPMw:adwords-kwoptimization=3l_zcGKkG-1JaIUb5gDALw:payments=L-B588QwA87bEP5rZT_Bhg:static_files=CP7Piuu05S0:maestro=HCDTqwjMwmc:explorer=Wr_pxbboSKkob2Ametjs_w:billing-ui=ta8p_9EHEyzM-t1B1_IB7Q:billing-ui-efe=ta8p_9EHEyzM-t1B1_IB7Q:billing-ui-v3=MQhyqIhWxgcE4vJ1UjMLtQ:billing-ui-v3-efe=MQhyqIhWxgcE4vJ1UjMLtQ; NID=67=twomnQxVWGcZe2Tv5O51aDywvrWw6IPVrb0eDlDFLcf-h702-pqMxC00T2zpWNdYpaOqD5bBwry9WLM59Ihm0J-xX-EbBEF92-yOIhbkfO0Z-evDQDyoP90MfW_RmMx0dYXUUMpgavAnkJqPV9HQnwyVaJB_syHzSeC1pnvLakuhqGmTs9CALgUz_rkbVyNKtyNyUfcGabfhlB_tBP9B4zHX3PbuFCKw0SRIp5OYryjqsBsdSb44s6-zwt1RBiVJYNwI00IR2yoQ8F0Qh_qR9aWg9WKfvSnMbTKTz5apkj_JZUFncE0laWGhlZ62eN6pvIZKf08Pq_wLOtwy9w; PREF=ID=49c02fa15de82d8a:U=ffc4e45e32b28a73:FF=0:LD=ru:NW=1:TM=1382696910:LM=1398547113:GM=1:SG=1:S=awJGfg65WzuRSWoX; SID=DQAAAPsBAAA9PbiIratUCiXJF6L0ts6bILjqk7qN4MJpMwzozMhhZ98VnkAOls2E0TuTRZc2T4jrVFVAQ5zBRMd1kmiTcZBQ5cYIU1fNbxi_6WyV9ol9kKpeXVibug-AdC1D8S3TaJC0iEem_ZDI7qoG4ud2cx1PVhH782joAJ2B1hFCpYSg7Eu_VAHPJTeUCwZFFOpEhMaIkOdzq7yd2l49GqHqggeopCXXcz8-9OYDDeAZUlqy6rr9rEO8nusvNumVJKCmHH9AgKoZlAx_p2G5l4LXGztOt4a7jyfXTgc_sQitJoSgCI2w0zIPNMvoTjvFkEZ0NFCa6RTqfK4VXYF7XHQoiOibD1PEZNrqsUgacqPRlMaDgU0GmQvcMPI8DfolQBjAXkU_KaJuW02pVBRusv1nxPvQZgJ3jFeEIW3EIabYr9UbZl-g0vsq9yM8MZ4q60oV_O1MzJPNitluV0moigWcvdpeUJvHb9_J8I8D8zNYXwznHufOcGjUeUdSN0nCdx2M3M4JwDaJRh7yywcppsWqV0qn-0kvUsdbBUaBRoeNV-8oydidMRMIPgo0MdASwz8FoGjAHNb0F2P8Fk8twlK5BRaTcamdlFM6F1CeWGFi7F5x886yGYFtHxz1SpgG8YCARR9VDHbBvVrTnq4FOwWPTeqbSukRfSxMd1Rgl2dXyoDPmg",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36",
    "x-client-data": "CMS1yQEIibbJAQijtskBCKm2yQEIxLbJAQi5iMoBCN6IygE="
}
url = "https://www.google.com/search?pz=1&cf=all&hl=en&tbm=nws&gl=en&as_q=kickstarter&as_occt=any&as_qdr=d&authuser=0"


def google_count():
    r = requests.get(url, headers=hdr)
    soup = BeautifulSoup(r.text.encode('utf-8'))
    line = str(soup.find("div", {"id": "resultStats"}))
    text = re.findall(r'About ([0-9]+,?[0-9]*) results', line)
    num = int(text[0].replace(',', ''))
    return num


def news_gather():
    db.connect()
    News.create(timestamp=int(time.time()),
                google_count=google_count(),
                twitter_count=twitter_count())
def show_time():
    return datetime.datetime.today().isoformat()