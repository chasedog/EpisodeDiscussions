from db import DB
import re
import nltk
import random
from nltk import classify

def getFeatures(post):
    hasSeasonAndEpisode = re.search(r'(Season|S)?:?\d{1,2}\s?,?\.?X?(Episode|Ep|E)?:?\d{1,2}', post["title"]) is not None and "Pre-" not in post["title"]
    return ({"hasSeasonAndEpisode": hasSeasonAndEpisode}, post["is_valid"])


conn = DB()

data = conn.getTrainingData()

random.shuffle(data)

train_set = [getFeatures(d) for d in data[:500]]

classifier = nltk.NaiveBayesClassifier.train(train_set)
classifier.show_most_informative_features(5)