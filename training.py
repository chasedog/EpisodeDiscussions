from db import DB
import nltk
import random
import classifiers

def getClassifier(all=True):
    conn = DB()

    data = conn.getTrainingData()

    random.shuffle(data)

    feature_sets = [(classifiers.getFeatures(d), "yes" if d["is_valid"] else "no") for d in data]
    if all:
        train_set, test_set = feature_sets, feature_sets
    else:
        train_set, test_set = feature_sets[:1500], feature_sets[1500:]

    classifier = nltk.NaiveBayesClassifier.train(train_set)
    classifier.show_most_informative_features(10)
    conn.close()
    print(nltk.classify.accuracy(classifier, test_set))
    return classifier

if __name__ == "__main__":
    classifier = getClassifier()

    conn = DB()
    #conn.create()

    data = conn.getTrainingData()
    for row in data:
        features = classifiers.getFeatures(row)
        is_valid = classifier.classify(features) == "yes"
        if row["is_valid"] != is_valid:
            print("{}->{} {} {}".format(row["is_valid"], is_valid, row["id"], row["title"]))
    conn.close()