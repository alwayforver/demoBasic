from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np


# def data_prep():
    

def simple_kmeans(docs, cluster = 2):

    vectorizer = TfidfVectorizer( stop_words='english')
    # vectorizer = TfidfVectorizer( stop_words=None)


    X = vectorizer.fit_transform(docs)

    km = KMeans(n_clusters=cluster, init='k-means++', max_iter=100, n_init=10,
                verbose=False)

    km.fit(X)
    # print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names()
    # for i in range(cluster):
    #     print("Cluster %d:" % i)
    #     for ind in order_centroids[i, :10]:
    #         print(' %s' % terms[ind])
    #     print

    row_sums = km.cluster_centers_.sum(axis=1)
    Pw_z = (km.cluster_centers_ / row_sums[:, np.newaxis]).T

    # print "Pw_z", Pw_z
    
    Pd = calc_Pd(docs)
    # print km.labels_
    Pz_d = calc_Pz_d_simple(km.labels_, cluster)

    # print Pw_z
    # print km.labels_, type(km.labels_)

    # print Pz_d

    return X, Pw_z, Pz_d, Pd, terms


def calc_Pd(docs):

    docs_term = []

    for doc in docs:
        doc_len = len(doc.split())

        docs_term.append(doc_len)

    sumV = sum(docs_term)

    Pd = [ float(x)/sumV  for x in docs_term]

    return np.array(Pd)
    

def calc_Pz_d_simple(labels, cluster):

    doc_length = len(labels)
    Pz_d = np.zeros((cluster,doc_length))
    Pz_d[:,:]=0.05

    normalized_1 = 1- (cluster-1)*0.05
    for i in xrange(doc_length):
        Pz_d[ labels[i], i]  = normalized_1

    return Pz_d



if __name__ == '__main__':
    simple_kmeans(['cat cat cat cat dog', 'dog dog dog dog dog dog dog cat dog', 'dog cat dog cat'])
    # print calc_Pd(['cat cat cat cat dog', 'dog dog dog dog dog dog dog cat dog', 'dog cat dog cat'])
    