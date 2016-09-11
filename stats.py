from db import DB
from itertools import groupby
import operator
from datetime import datetime
import classifiers, re


def contains(word, capture):
    return 1 if word in capture else 0

def printEpisodes(data):
    for item in data:
        titleLowered = item["title"].lower()
        matches = re.findall(classifiers.ff, titleLowered)
        count = len(matches)
        if count == 0:
            item["season"] = -1
            item["episode"] = -1
        elif count == 1:
            #print(matches)
            if len(matches[0][0]):
                item["season"] = int(matches[0][0][0])
                item["episode"] = int(matches[0][0][1:])
            else:
                item["season"] = int(matches[0][2])
                item["episode"] = int(matches[0][4])
        else:
            scores = {}

            for idx, match in enumerate(matches):
                capture = match[0].lower()
                print(match)
                scores[idx] = sum([contains(score, capture) for score in [".", "s", "e", "x"]])
            maxScore = max(scores.keys(), key=(lambda key: scores[key]))

            print("max",scores)
            item["season"] = int(matches[maxScore][2])
            item["episode"] = int(matches[maxScore][4])

        print(item["season"], item["episode"], item["title"])

        episodeName = re.search(classifiers.somethingInQuotesRegex, item["title"])
        item["episodeName"] = None if episodeName is None else episodeName.group(0)
        flair = "" if item["link_flair_text"] is None else item["link_flair_text"].lower()
        if re.search(r"re-?watch", titleLowered) is not None or re.search(r"re-?watch", flair) is not None:
            item["isRewatch"] = True
        else:
            item["isRewatch"] = False

    data = sorted(data, key=lambda x: (x["subreddit"], x["season"], x["isRewatch"], x["episode"], x["created_utc"]))

    for subreddit, group in groupby(data, lambda x: x["subreddit"]):
        print(subreddit)
        #subredditSorted = sorted(group, key=lambda x: (x["season"], x["episode"], x["created_utc"]))
        for season, seasonGroup in groupby(group, lambda x: (x["season"], x["isRewatch"])):
            print(" Season {}{}".format(season[0], " Rewatch:" if season[1] else ":"))
            #sortedEpisodes = sorted(seasonGroup, key=lambda x: (x["episode"], x["created_utc"]))

            for item in seasonGroup:
                date = datetime.utcfromtimestamp(item["created_utc"]).strftime("%m/%d/%Y")
                if not item["episodeName"]:
                    print("  {}. {} {} - {}".format(item["episode"], item["title"], date, item["url"]))
                else:
                    print("  {}. {} {} - {}".format(item["episode"], item["episodeName"], date, item["url"]))

if __name__ == "__main__":
    conn = DB()
    data = conn.getValidDiscussionData()
    printEpisodes(data)
    conn.close()