import praw
import db
from db import DB
import classifiers
import training

conn = DB()

user_agent = "EpisodeDiscussions 1.0 by chasedog"

reddit = praw.Reddit(user_agent=user_agent)

#posts = reddit.search("title:episode discussion flair:'Season 1'", subreddit="gameofthrones", sort="new", limit=20)
#posts = reddit.search("flair:discussion", subreddit="raydonovan", sort="new", limit=100)
#posts = reddit.search("episode discussion", subreddit="southpark", sort="relevance", limit=500)
#posts = reddit.search("discussion", subreddit="breakingbad", sort="relevance", limit=500)
posts = reddit.search("discussion OR thread", subreddit="suits", sort="relevance", limit=1500)

insertData = []
columns = db.tables[0]["columns"]
def mapToDict(data):
    dataDict = {}
    columns = [c for c in db.tables[0]["columns"] if "ignore" not in c]

    for idx, column in enumerate(columns):
        dataDict[column["db"]] = data[idx]

    return dataDict

if __name__ == "__main__":
    import stats
    classifier = training.getClassifier()

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
            data = (is_valid,) + tuple(tupledData)
            insertData.append(dataDict)

    stats.printEpisodes(insertData)
#print([(d[0],d[2]) for d in insertData])
#conn.insertManyTrainingData(insertData)