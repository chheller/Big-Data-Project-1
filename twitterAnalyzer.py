import time
import datetime
from pymongo import MongoClient
import json
import bson

####################
#References:
#Opinion dataset
#Minqing Hu and Bing Liu. "Mining and Summarizing Customer Reviews."
#       Proceedings of the ACM SIGKDD International Conference on Knowledge
#       Discovery and Data Mining (KDD-2004), Aug 22-25, 2004, Seattle,
#       Washington, USA,
#   Bing Liu, Minqing Hu and Junsheng Cheng. "Opinion Observer: Analyzing
#       and Comparing Opinions on the Web." Proceedings of the 14th
#       International World Wide Web conference (WWW-2005), May 10-14,
#       2005, Chiba, Japan.#
#
#   https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html#lexicon
###################

client = MongoClient('localhost', 27017)
db = client['twitter_db']

positiveWords = set()
negativeWords = set()

with open("positive-words.txt") as filein:
    for word in filein:
        positiveWords.add(word[0:len(word)-1])
with open("negative-words.txt") as filein:
    for word in filein:
        negativeWords.add(word[0:len(word)-1])


searchQuery = ["#Election2016",'#news', '#politics', '#BREAKING' ]



def Analyzer(searchQuery):
    outputFile = open("output.txt", "w+")
    clin_aggr = 0
    trump_aggr = 0
    trump_pos = 0
    trump_neg = 0
    clin_pos = 0
    clin_neg = 0
    clin_count = 0
    trump_count = 0
    all_tweets = 0
    for query in searchQuery:
        collection = db['twitter_{0}'.format(query[1:])]
        for tweets in collection.find():
            all_tweets += 1
            posCount = 0
            negCount = 0
            rating = 0
            body = tweets['text'].lower().split(' ')

            if ("clinton" in body or "trump" in body) and not ("clinton" in body and "trump" in body):
                for words in body:
                    if words in positiveWords:
                        posCount += 1
                        rating += 1
                    if words in negativeWords:
                        negCount += 1
                        rating -= 1
                if "clinton" in body:
                    clin_pos += posCount
                    clin_neg += negCount
                    candidate = "clinton"
                    clin_count += 1
                    if rating > 0:
                        clin_aggr += 1
                    elif rating < 0:
                        clin_aggr -= 1
                else:
                    candidate = "trump"
                    trump_count += 1
                    trump_pos += posCount
                    trump_neg += negCount
                    if rating > 0:
                        trump_aggr += 1
                    elif rating < 0:
                        trump_aggr -= 1
                output = """
            Tweet ID: {0}
            Candidate: {1}
            Total positive: {2}
            Total negative: {3}
            Average: {4}
            *-----------------------------------*
            """.format(tweets['_id'], candidate, posCount, negCount, posCount-negCount)
                outputFile.write(output)



    aggregate = open("aggr_out.txt", "w+")
    aggr_out = """

                    Trump         | Clinton
    ----------------------------------------------------------
    Total Positive: {0}                 | {1}
    Total Negative: {2}                 | {3}
    Net Score:      {4}                 | {5}
    Average Score:  {6:.2f}             | {7:.2f}
    Total Tweets:   {8}                 | {9}
    -----------------------------------------------------------
    Total Tweets: {10}
    All Tweets: {11}
    """.format(trump_pos, clin_pos, trump_neg, clin_neg, trump_aggr, clin_aggr,
               trump_aggr/trump_count, clin_aggr/clin_count, trump_count, clin_count,
               clin_count+trump_count, all_tweets)
    aggregate.write(aggr_out)
    print(aggr_out)
def CleanDatabase(searchQuery):
    for query in searchQuery:
        collection = db['twitter_{0}'.format(query[1:])]
        for tweets in collection.find():
            body = tweets['text'].lower().split(" ")

            if "clinton" not in body and "trump" not in body:
                collection.remove(tweets["_id"])


#CleanDatabase(searchQuery)

Analyzer(searchQuery)



