import re
import numpy as np
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

stopwords = ["is", "the", "a", "an", "to", "for", "of"]

def tokenize(sentence):
    sentence = sentence.lower()
    sentence = re.sub(r'[^a-zA-Z0-9\s]', '', sentence)
    tokens = sentence.split()
    return [w for w in tokens if w not in stopwords]

def stem(word):
    return stemmer.stem(word.lower())

def bag_of_words(tokenized_sentence, words):
    sentence_words = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(words), dtype=np.float32)

    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1

    return bag