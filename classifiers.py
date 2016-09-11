import re
from datetime import datetime, timedelta
from enum import Enum
from inspect import ismethod

somethingInQuotesRegex = r"""("[^"]+"|'[^']+'|”[^”]+”)"""
ff =              r'(((?:season|s)?\s?:?(\d{1,2}))\s?,?-?\s?\.?x?((?:episode|ep|e)?\s?:?0*(\d{1,2})))'
formattedSERegex = r'((?:season|s)?\s?:?(\d{1,2}))\s?,?-?\s?\.?x?((?:episode|ep|e)?\s?:?0*(\d{1,2}))'

class PostTitleClassifiers:
    def containsSurveyResults(self, title):
        return "survey results" in title

    def containsBest(self, title):
        return "best"

    def containsMegathread(self, title):
        return "megathread" in title

    def containsRewatch(self, title):
        return "rewatch" in title

    def containsSomethingInQuotes(self, title):
        return re.search(somethingInQuotesRegex, title) is not None

    def containsSomethingInQuotesPlusDiscussion(self, title):
        return re.search(r"""("[^"]+"|'[^']+')\sdiscussion""", title) is not None
    def containsDash(self, title):
        return " - " in title

    def containsPostStuff(self, title):
        return re.search(r'(post-|\spost\s)', title) is not None

    def containsPrediction(self, title):
        return "prediction" in title

    def containsPreStuff(self, title):
        return re.search(r'(predictions|prediction|pre\s|pre-)', title) is not None

    def containsEpisodeDiscussion(self, title):
        return "episode discussion" in title

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

    def containsFormattedSE(self, string):
        return re.search(r'%s' % formattedSERegex, string) is not None

    def containsFormattedSEPlusDiscussion(self, string):
        return re.search(r'((?:season|s)?\s?:?\d{1,2})\s?,?\.?x?((?:episode|ep|e)?\s?:?\d{1,2})\sdiscussion', string) is not None

    def endsWithExclamationPoint(self, string):
        return string[-1] == '!'

class TimeBucket(Enum):
    morning = 0
    afternoon = 1
    primetime = 2
    latenight = 3

class ScoreBucket(Enum):
    really_low = 0
    low = 1
    medium = 2
    high = 3


class PostClassifiers:

    def getTimeBucket(self, post):
        easternTime = datetime.utcfromtimestamp(post["created_utc"]) - timedelta(hours=8)
        hour = easternTime.hour
        if hour >= 5 and hour < 12:
            return TimeBucket.morning
        elif hour >= 12 and hour < 16:
            return TimeBucket.afternoon
        elif hour >= 16 and hour < 21:
            return TimeBucket.primetime
        return TimeBucket.latenight

    def flairContainsDiscussion(self, post):
        return post["link_flair_text"] is not None and "discussion" in post["link_flair_text"]

    def isAutoModerator(self, post):
        return post["author"] == "AutoModerator"

    def isArchived(self, post):
        return post["archived"]

    def isSelfPost(self, post):
        return post["is_self"]

    def score(self, post):
        score = post["score"]
        if score < 5:
            return ScoreBucket.really_low
        if score < 15:
            return ScoreBucket.low
        if score < 50:
            return ScoreBucket.medium
        return ScoreBucket.high

def iterateThroughMethods(features, post, postTitleClassifiers):
    for function in dir(postTitleClassifiers):
        theFunc = getattr(postTitleClassifiers, function)
        if ismethod(theFunc):
            features[function] = theFunc(post)


def getFeatures(post):
    features = {}

    postTitleClassifiers = PostTitleClassifiers()
    postClassifiers = PostClassifiers()

    iterateThroughMethods(features, post["title"].lower(), postTitleClassifiers)
    iterateThroughMethods(features, post, postClassifiers)

    return features

