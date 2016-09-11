from db import DB
from itertools import groupby
import operator
from datetime import datetime, timedelta
import classifiers, re

class Season:
    def __init__(self, number, isRewatch):
        self.number = number
        self.episodes = []
        self.is_rewatch = isRewatch

    def addEpisode(self, episode):
        self.episodes.append(episode)

    def serialize(self):
        return {
            'season_number': self.number,
            'episodes': [e.serialize() for e in self.episodes],
            'is_rewatch': self.is_rewatch
        }

class Episode:
    def __init__(self, title, url, number, date_utc, name):
        self.name = name
        self.title = title
        self.url = url
        self.number = number
        self.date_utc = date_utc
        self.date_pacific = (datetime.utcfromtimestamp(self.date_utc) - timedelta(hours=7)).strftime("%m/%d/%Y")

        titleLowered = title.lower()
        containsPre = " pre" in titleLowered
        containsPost = " post" in titleLowered
        self.prePostText = "pre" if containsPre else "post" if containsPost else ""

    def serialize(self):
        return {
            'name': self.name,
            'title': self.title,
            'url': self.url,
            'episode_number': self.number,
            'date_utc': self.date_utc,
            'date_pacific': self.date_pacific
        }

def contains(word, capture):
    return 1 if word in capture else 0

def extractSeasonsAndEpisodes(data):
    for item in data:
        titleLowered = item["title"].lower()
        matches = re.findall(classifiers.ff, titleLowered)
        count = len(matches)
        if count == 0:
            item["season"] = -1
            item["episode"] = -1
        elif count == 1:
            season = matches[0][2].strip()
            episode = matches[0][4].strip()
            seasonAndEpisode = str(season) + episode

            if len(season) >= 1 and len(episode) >= 1:
                print("A", matches[0])
                item["season"] = int(season)
                item["episode"] = int(episode)
            elif len(matches[0][0].strip()) <= 2 and len(seasonAndEpisode) <= 2:
                print("B", matches[0])
                item["season"] = -1
                item["episode"] = -1
            else:
                print("C", matches[0])
                item["season"] = int(seasonAndEpisode[0])
                item["episode"] = int(seasonAndEpisode[1:])
        else:
            scores = {}

            for idx, match in enumerate(matches):
                capture = match[0].lower()
                scores[idx] = sum([contains(score, capture) for score in [".", "s", "e", "x"]])
            maxScore = max(scores.keys(), key=(lambda key: scores[key]))

            item["season"] = int(matches[maxScore][2])
            item["episode"] = int(matches[maxScore][4])

        #print(item["season"], item["episode"], item["title"])

        episodeName = re.search(classifiers.somethingInQuotesRegex, item["title"])
        item["episodeName"] = None if episodeName is None else episodeName.group(0)
        flair = "" if item["link_flair_text"] is None else item["link_flair_text"].lower()
        if re.search(r"re-?watch", titleLowered) is not None or re.search(r"re-?watch", flair) is not None:
            item["isRewatch"] = True
        else:
            item["isRewatch"] = False

    data = sorted(data, key=lambda x: (x["subreddit"], x["season"], x["isRewatch"], x["episode"], x["created_utc"]))

    response = []
    for subreddit, group in groupby(data, lambda x: x["subreddit"]):
        #subredditSorted = sorted(group, key=lambda x: (x["season"], x["episode"], x["created_utc"]))
        for season, seasonGroup in groupby(group, lambda x: (x["season"], x["isRewatch"])):
            #sortedEpisodes = sorted(seasonGroup, key=lambda x: (x["episode"], x["created_utc"]))
            season = Season(season[0], season[1])
            for item in seasonGroup:
                episode = Episode(item["title"], item["url"], item["episode"], item["created_utc"], item["episodeName"])
                season.addEpisode(episode)
                #date = datetime.utcfromtimestamp(item["created_utc"]).strftime("%m/%d/%Y")

            response.append(season)

    return response

if __name__ == "__main__":
    conn = DB()
    data = conn.getValidDiscussionData()
    extractSeasonsAndEpisodes(data)
    conn.close()