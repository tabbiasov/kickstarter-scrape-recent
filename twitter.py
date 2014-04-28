import sys
sys.path.insert(0, 'libs')

#Import the required modules
from twython import Twython

#Set parameters
keyword = 'kickstarter'; #The desired keyword(s)
tweetsXiteration = 100; #Where 100 is the max
dateFrom = '2014-04-26'; #Inclusive (YYYY-MM-DD)
dateTo = '2014-04-27'; #Exclusive (YYYY-MM-DD)
done = False; #Must be false

#Setting the OAuth
Consumer_Key = '0Io4CpjhioOrhvsUV4JFNDhER';
Consumer_Secret = '0CIK7WinLIys6RqrthW4tZ1naKqT5t0xkEkUD7mgjhkjETxKt2';
Access_Token = '297465676-tYLgZxyI5tUxkBOZkzu2LR3jNKZXQhLopPpCwmJi';
Access_Token_Secret = 'lDmvxgN0mpxgXEVjQrqROGPwvv4xvctiyGCNLnhmPOEsY';


def count():
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