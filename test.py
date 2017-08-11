import praw
import db
from db import DB
import classifiers
import training
import stats

conn = DB()

user_agent = "EpisodeDiscussions 1.0 by chasedog"

reddit = praw.Reddit(user_agent=user_agent, client_secret="onbDi1nT26b-5lATWO-hRQJyTM8", client_id="GoA8FYqBzRTY2g")

#posts = reddit.search("title:episode discussion flair:'Season 1'", subreddit="gameofthrones", sort="new", limit=20)
#posts = reddit.search("flair:discussion", subreddit="raydonovan", sort="new", limit=100)
#posts = reddit.search("episode discussion", subreddit="southpark", sort="relevance", limit=500)
#posts = reddit.search("discussion", subreddit="breakingbad", sort="relevance", limit=500)

def mapToDict(data):
    dataDict = {}
    columns = [c for c in db.tables[0]["columns"] if "ignore" not in c]

    for idx, column in enumerate(columns):
        dataDict[column["db"]] = data[idx]

    return dataDict

def getPostsFromReddit(subreddit):
    """
    Retrieves posts from the specified subreddit via a reddit search.
    :param subreddit:
    :return:
    """

    posts = reddit.subreddit(subreddit).search("discussion OR thread", sort="relevance", limit=1500)
    return posts


def deserializePostToEpisodeDiscussion(post):
    """
    Deserializes a reddit post into an episode discussion object based on our database schema.
    :param post:
    :return:
    """

    columns = db.tables[0]["columns"]
    columnsNotIgnored = [column for column in columns if "ignore" not in column]

    tupledData = []
    dataDict = {}

    for column in columnsNotIgnored:
        fieldName = column["db"][0]

        if "mapper" not in column:
            value = getattr(post, fieldName)
        else:
            value = getattr(getattr(post, fieldName), column["mapper"])

        tupledData.append(value)
        dataDict[fieldName] = value

    return dataDict, tupledData

def getValidData(subreddit):
    """
    Retrieves episode discussions from the specified subreddit.
    :param subreddit:
    :return:
    """

    posts = getPostsFromReddit(subreddit)

    insertData = []
    classifier = training.getClassifier()

    for post in posts:
        dataDict, tupledData = deserializePostToEpisodeDiscussion(post)

        features = classifiers.getFeatures(dataDict)

        is_valid = classifier.classify(features) == "yes"

        if is_valid:
            insertData.append(dataDict)
    return insertData

if __name__ == "__main__":
    data = getValidData("madmen")
    #stats.extractSeasonsAndEpisodes(data)
    #print(data)
    print([(d[0],d[2]) for d in data])
    #conn.insertManyTrainingData(data)