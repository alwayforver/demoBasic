from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import metrics
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np
from scipy.sparse import csr_matrix, coo_matrix


# def data_prep():
    
 
def simple_kmeans(X, cluster = 2):

    km = KMeans(n_clusters=cluster, init='k-means++', max_iter=100, n_init=10,
                verbose=False)

    km.fit(X)
    # print("Top terms per cluster:")
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    
    # for i in range(cluster):
    #     print("Cluster %d:" % i)
    #     for ind in order_centroids[i, :10]:
    #         print(' %s' % terms[ind])
    #     print
    row_sums = km.cluster_centers_.sum(axis=1)
    Pw_z = (km.cluster_centers_ / row_sums[:, np.newaxis]).T

    # print "Pw_z", Pw_z
    # print km.labels_
    Pz_d = calc_Pz_d_simple(km.labels_, cluster)

    # print Pw_z
    # print km.labels_, type(km.labels_)

    # print Pz_d
    return Pw_z, Pz_d, km.labels_


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

def calc_Pe_z(labels, Xe, cluster_num):
    # print "in function",type(Xe), np.shape(Xe)

    Xe = Xe.tocoo()

    # print "in function",type(Xe), np.shape(Xe)

    doc_num  = len(labels)
    row = []
    column = []
    value = []

    for i in xrange(len(Xe.row)):
        e = Xe.col[i]
        z = labels[Xe.row[i]]

        row.append(e)
        column.append(z)
        value.append(Xe.data[i])

    # print labels


    # for i in xrange(doc_num):
    Pe_z = coo_matrix( ( value, ( row, column )), shape= ( np.shape(Xe)[1], cluster_num) ).toarray()
    




    return Pe_z




if __name__ == '__main__':
    simple_kmeans(['cat cat cat cat dog', 'dog dog dog dog dog dog dog cat dog', 'dog cat dog cat'])
    # print calc_Pd(['cat cat cat cat dog', 'dog dog dog dog dog dog dog cat dog', 'dog cat dog cat'])
    