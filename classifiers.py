import re
import datetime
from enum import Enum
from inspect import ismethod

class PostTitleClassifiers:
    def containsDiscussion(self, string):
        return "discussion" in string

    def containsThread(self, string):
        return "thread" in string

    def containsSeason(self, string):
        return "season" in string

    def containsEpisode(self, string):
        return "episode" in string

    def containsSpoiler(self, string):
        return "spoiler" in string

    def endsWithQuestionMark(self, string):
        return string[-1] == '?'

    def containsFormattedSeasonAndEpisode(self, string):
        return re.search(r'(season|s)?:?\d{1,2}\s?,?\.?x?(episode|ep|e)?:?\d{1,2}', string) is not None

    def endsWithExclamationPoint(self, string):
        return string[-1] == '!'

class TimeBucket(Enum):
    night = 0
    morning = 1
    afternoon = 2
    evening = 3

def getTimeBucket(post):
    postHour = (datetime.datetime.utcfromtimestamp(post["created_utc"])).hour
    postTimeBucket = int(float(postHour) / 6)
    return TimeBucket(postTimeBucket)

def getFeatures(post):
    features = {}

    postTitleClassifiers = PostTitleClassifiers()
    for function in dir(postTitleClassifiers):
        attribute = getattr(postTitleClassifiers, function)
        if ismethod(attribute):
            features[function] = attribute(post["title"].lower())

    return features

fakePost1 = { "created_utc" : 1472429218, "title" : "My Amazing Episode Discussion" }
print(getTimeBucket(fakePost1))
print(getFeatures(fakePost1))
