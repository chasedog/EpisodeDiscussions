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



columns = db.tables[0]["columns"]

def mapToDict(data):
    dataDict = {}
    columns = [c for c in db.tables[0]["columns"] if "ignore" not in c]

    for idx, column in enumerate(columns):
        dataDict[column["db"]] = data[idx]

    return dataDict

def getValidData(subreddit):
    insertData = []
    classifier = training.getClassifier()
    posts = reddit.subreddit(subreddit).search("discussion OR thread", sort="relevance", limit=1500)
    for post in posts:
        tupledData = []
        dataDict = {}
        for column in [column for column in columns if "ignore" not in column]:
            fieldName = column["db"][0]
            value = getattr(post, fieldName) if "mapper" not in column else getattr(getattr(post, fieldName), column["mapper"])
            tupledData.append(value)
            dataDict[fieldName] = value

        features = classifiers.getFeatures(dataDict)

        is_valid = classifier.classify(features) == "yes"

        if is_valid:
            insertData.append(dataDict)
    return insertData

def getData(subreddit):
    insertData = []
    classifier = training.getClassifier()
    posts = reddit.subreddit(subreddit).search("discussion OR thread", sort="relevance", limit=1500)
    for post in posts:
        tupledData = []
        dataDict = {}
        for column in [column for column in columns if "ignore" not in column]:
            fieldName = column["db"][0]
            value = getattr(post, fieldName) if "mapper" not in column else getattr(getattr(post, fieldName), column["mapper"])
            tupledData.append(value)
            dataDict[fieldName] = value

        features = classifiers.getFeatures(dataDict)

        is_valid = classifier.classify(features) == "yes"

        data = (is_valid,) + tuple(tupledData)
        insertData.append(data)
    return insertData

if __name__ == "__main__":
    data = getData("madmen")
    #stats.extractSeasonsAndEpisodes(data)
    #print(data)
    print([(d[0],d[2]) for d in data])
    #conn.insertManyTrainingData(data)