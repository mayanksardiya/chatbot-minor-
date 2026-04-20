import json
import pickle
import numpy as np
from sklearn.neural_network import MLPClassifier
from utils.nlp_utils import tokenize, stem, bag_of_words

with open("intents.json") as file:
    data = json.load(file)

all_words = []
tags = []
xy = []

for intent in data["intents"]:
    tag = intent["tag"]
    tags.append(tag)

    for pattern in intent["patterns"]:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

ignore_words = ["?", "!", "."]
all_words = sorted(set([stem(w) for w in all_words if w not in ignore_words]))
tags = sorted(set(tags))

X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    y_train.append(tags.index(tag))

model = MLPClassifier(
    hidden_layer_sizes=(16, 16),
    activation='relu',
    solver='adam',
    max_iter=1500
)

model.fit(X_train, y_train)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(all_words, open("words.pkl", "wb"))
pickle.dump(tags, open("classes.pkl", "wb"))

print("Model trained and saved")