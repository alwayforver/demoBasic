import numpy as np
from scipy.sparse import csr_matrix, coo_matrix
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)

l = [ "cat, dog: is good cat","try this dog. cat,"    ]

vectorizer.fit_transform(l)

print vectorizer.get_feature_names()
