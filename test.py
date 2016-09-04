import praw
import datetime
import db
from db import DB
import re
conn = DB()

user_agent = "EpisodeDiscussions 1.0 by chasedog"

reddit = praw.Reddit(user_agent=user_agent)

#posts = reddit.search("title:episode discussion flair:'Season 1'", subreddit="gameofthrones", sort="new", limit=20)
#posts = reddit.search("flair:discussion", subreddit="raydonovan", sort="new", limit=100)
#posts = reddit.search("episode discussion", subreddit="southpark", sort="relevance", limit=500)
posts = reddit.search("discussion", subreddit="breakingbad", sort="relevance", limit=100)

insertData = []
columns = db.tables[0]["columns"]

for post in posts:
    data = tuple([getattr(post, column["db"][0]) if "mapper" not in column else getattr(getattr(post, column["db"][0]), column["mapper"]) for column in columns if "ignore" not in column])

    is_valid = re.search(r'S?\d{1,2}\.?X?E?\d{1,2}', data[1]) is not None
    data = (is_valid,) + data
    insertData.append(data)

print([(d[0],d[2]) for d in insertData])
conn.insertManyTrainingData(insertData)