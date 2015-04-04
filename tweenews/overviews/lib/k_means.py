from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np
from scipy.sparse import csr_matrix, coo_matrix


# def data_prep():


def simple_kmeans(X, cluster=2):

    km = KMeans(n_clusters=cluster, init='k-means++', max_iter=100, n_init=10,
                verbose=False)
    km.fit(X)
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    row_sums = km.cluster_centers_.sum(axis=1)
    Pz_d = calc_Pz_d_simple(km.labels_, cluster)

    nWords = X.shape[1]
    C = km.cluster_centers_.T+1.0/nWords/nWords
    Pw_z = C/np.tile(sum(C),(nWords,1))

    return Pw_z, Pz_d, km.labels_


def calc_Pd(docs):

    docs_term = []

    for doc in docs:
        doc_len = len(doc.split())

        docs_term.append(doc_len)
    sumV = sum(docs_term)

    Pd = [float(x) / sumV for x in docs_term]

    return np.array(Pd)


def calc_Pz_d_simple(labels, cluster):

    doc_length = len(labels)
    Pz_d = np.zeros((cluster, doc_length))
    Pz_d[:, :] = 0

    # normalized_1 = 1 - (cluster - 1) * 0.05

    for i in xrange(doc_length):
        Pz_d[labels[i], i] = 1

    Pz_d += 0.1
    Pz_d /= np.tile(Pz_d.sum(axis=0),(cluster,1))
    return Pz_d


def calc_Pe_z(labels, Xe, cluster_num):
    # print "in function",type(Xe), np.shape(Xe)

    # Xe = Xe.tocoo()

    # # print "in function",type(Xe), np.shape(Xe)

    # # doc_num = len(labels)
    # row = []
    # column = []
    # value = []

    # for i in xrange(len(Xe.row)):
    #     e = Xe.col[i]
    #     z = labels[Xe.row[i]]

    #     row.append(e)
    #     column.append(z)
    #     value.append(Xe.data[i])

    # # print labels

    # # for i in xrange(doc_num):
    # Pe_z = coo_matrix(
    #     (value, (row, column)), shape=(np.shape(Xe)[1], cluster_num)).toarray()
    # print type(labels)
    Xe = Xe.tocsr()
    nEnt = Xe.shape[1]
    Pe_z = np.zeros((nEnt,cluster_num))
    for i in xrange(cluster_num):
        Pe_z[:,i] = Xe[labels==i,:].mean(0)
    # print "pass"
    C = Pe_z+1e-7 #1.0/nEnt/nEnt
    Pe_z = C/np.tile(sum(C),(nEnt,1))
    return Pe_z


def km_initialize(X, Xe, entityTypes, cluster_num):
    Pw_z_km, Pz_d_km, labels_km = simple_kmeans(X, cluster_num)
    Pe_z_km = {}
    for each_type in entityTypes:
        Pe_z_km[each_type] = calc_Pe_z(labels_km, Xe[each_type], cluster_num)

    inits_notime = [Pz_d_km, Pw_z_km]
    for each_type in entityTypes:
        inits_notime.append(Pe_z_km[each_type])
    return inits_notime, labels_km


if __name__ == '__main__':
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10000)
    X = vectorizer.fit_transform(['cat cat cat cat dog','cat cat cat catdog dog', 'dog dog dog dog dog dog dog cat dog', 'dog cat dog cat'])

    simple_kmeans(X, 2)
    # print calc_Pd(['cat cat cat cat dog', 'dog dog dog dog dog dog dog cat
    # dog', 'dog cat dog cat'])
