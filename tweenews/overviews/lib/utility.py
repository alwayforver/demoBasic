import time
from datetime import datetime, timedelta
from django.utils import timezone
import numpy as np
from scipy.sparse import csr_matrix, coo_matrix


class PLSACache:

    def __init__(self):
        self.data = []

    def __init__(self, Xdata, Pw_zs, n_wdxPz_wds, ind2obj, terms, reverse_voc, vectorizer):
        self.Xdata = Xdata
        self.Pw_zs = Pw_zs
        self.n_wdxPz_wds = n_wdxPz_wds
        self.ind2obj = ind2obj
        self.terms = terms
        self.reverse_voc = reverse_voc
        self.vectorizer = vectorizer



def data_prep(news_list, ind2obj):
    raw_docs = []
    count = 0
    for each in news_list:
        # raw_docs.append(each.title)
        raw_docs.append(each.title + ' ' + each.raw_text)
        ind2obj[count] = each
        count += 1
    return raw_docs


def parse_date(date_str):
    # in the form of 2015-01-01
    date_str = date_str[2:]
    if '-' in date_str:
        try:
            to_return = datetime.strptime(date_str, '%y-%m-%d')
        except:
            return None
    else:
        try:

            to_return = datetime.strptime(date_str, '%y%m%d')
        except:
            return None

    return timezone.make_aware(to_return, timezone.get_default_timezone())


def prepend_date(start, end, to_write):
    return start + ':' + end + ':' + to_write


def find_toptitle_simple(Pz_d, ind2obj, top_n):
    cluster = Pz_d.shape[0]-1
    ordered_ind = Pz_d.argsort(axis=1)[:, ::-1][:, :top_n]
    top_title = []

    for i in xrange(cluster):
        this = []
        for j in xrange(top_n):
            this.append(ind2obj[ordered_ind[i, j]].title)
        top_title.append(this)
    return top_title


def find_toptitle_dID(Pz_d, ind2obj, top_n, dID):
    # background elimination
    cluster = Pz_d.shape[0]-1

    ordered_ind = Pz_d.argsort(axis=1)[:, ::-1][:, :top_n]
    top_title = []

    for i in xrange(cluster):
        this = []
        for j in xrange(top_n):
            this.append(ind2obj[dID[ordered_ind[i, j]]].title)
        top_title.append(this)
    return top_title


def find_topterms_simple(Pw_z, terms, top_n):
    cluster = Pw_z.shape[1]-1

    ordered_ind = Pw_z.argsort(axis=0)[::-1, :][:top_n, :]
    top_term = []

    for i in xrange(cluster):
        this = []
        for j in xrange(top_n):
            this.append(terms[ordered_ind[j, i]])
        top_term.append(this)
    return top_term

def find_topterms_dic(Pw_z, terms, top_n):
    cluster = Pw_z.shape[1]-1

    ordered_ind = Pw_z.argsort(axis=0)[::-1, :][:top_n, :]
    top_term_dic = []
    for i in xrange(cluster):
        this = {}
        for j in xrange(top_n):
            this[terms[ordered_ind[j, i]]] = Pw_z[ordered_ind[j, i], i]
        top_term_dic.append(this)
    return top_term_dic

def parse_entity_str(entity_str):
   
    result = {}
    result['place'] = {}
    result['org'] = {}
    result['person'] = {}

    if entity_str==None:
        print "non_entity_str!"
        return result

    entities = entity_str.strip().split(';')

    for entity in entities:
        fields = entity.split(':')
        if len(fields) != 3:
            continue
        result[fields[1]][fields[0]] = int(fields[2])
        if fields[2]=="":
            continue
    return result


def calc_entity_matrix(news_entities, entityTypes):

    # entityTypes = ['person','org', 'place']
    X = {}
    count = {}
    voc = {}
    reverse_voc = {}
    mrow = {}
    mcolumn = {}
    mvalue = {}

    for each_type in entityTypes:

        count[each_type] = 0
        voc[each_type] = {}
        mrow[each_type] = []
        mcolumn[each_type] = []
        mvalue[each_type] = []
        reverse_voc[each_type] = []

    cat_ent_cnt_list = []

    for entity_str in news_entities:
        cat_ent_cnt_list.append(parse_entity_str(entity_str))

    for cat_ent_cnt in cat_ent_cnt_list:
        for each_type in entityTypes:
            all_type_values = cat_ent_cnt[each_type].keys()
            for type_value in all_type_values:
                if type_value not in voc[each_type]:
                    voc[each_type][type_value] = count[each_type]
                    reverse_voc[each_type].append(type_value)
                    count[each_type] += 1

    doc_count = 0
    for cat_ent_cnt in cat_ent_cnt_list:
        for each_type in entityTypes:
            for ent, cnt in cat_ent_cnt[each_type].iteritems():
                mrow[each_type].append(doc_count)
                mcolumn[each_type].append(voc[each_type][ent])
                mvalue[each_type].append(cnt)
        doc_count += 1

    for each_type in entityTypes:
        X[each_type] = coo_matrix((mvalue[each_type], (mrow[each_type], mcolumn[
                                  each_type])), shape=(doc_count, len(reverse_voc[each_type]))).tocsr()

    return X, reverse_voc


def inittime(DT, K, labels):
    mu = np.zeros(K)
    sigma = np.zeros(K)
    for i in range(K):
        ts = np.array(DT)[labels == i]
        mu[i] = np.mean(ts)
        sigma[i] = np.std(ts)
    return mu, sigma


def get_ticks(exact_time):
    return (exact_time - timezone.make_aware(datetime(1970, 1, 1), timezone.get_default_timezone())).total_seconds()


def weightX(X, Pw_z, Pz_d):
    K = Pz_d.shape[0]
    X = X.tocoo()
    docind, wordind, value = (X.row, X.col, X.data)
    # Pz_do_f = Pz_do.*(Pz_do>(1-lambdaB)/double(K-1))
    Pz_d_f = Pz_d  * (Pz_d > 0.01)
    Pz_dw_ = Pw_z[wordind, :].T * Pz_d_f[:, docind]
    Pw_d = Pz_dw_.sum(axis=0)  # 1 x nnz
    Pz_wd = Pz_dw_[:-1, :] / np.tile(Pw_d, (K - 1, 1))
    n_wdxPz_wd = np.tile(value, (K - 1, 1)) * Pz_wd
    n_wdxPz_wd = n_wdxPz_wd * (n_wdxPz_wd > 0.0001)
    return n_wdxPz_wd

# get event matrices
def selectTopic(Xs, n_wdxPz_wds, event):
    Xevents = []
    for i in range(len(Xs)):
        X = Xs[i]
        X = X.tocoo()

        n_wdxPz_wd = n_wdxPz_wds[i]
        nDocs, nWords = X.shape
        docind, wordind, value = (X.row, X.col, X.data)
        value = n_wdxPz_wd[event, :]
        # select = (value != 0)
        select = (value >0.2*max(value))
        value_f = value[select]
        row_f = docind[select]  # 1 3 3 5 5 6 6 6
        col_f = wordind[select]
        if i == 0:
            dID = np.unique(row_f)  # 1 3 5 6
        dID2ind = -np.ones(nDocs)  # -1 -1 -1 -1 -1 -1 -1 assume nDocs = 7
        dID2ind[dID] = np.arange(len(dID))  # 0 0 1 0 2 3 0
        row_f_new = dID2ind[row_f]  # 0 1 1 2 2 3 3 3
        if i > 0:
            select = (row_f_new != -1)
            Xevent = coo_matrix(
                (value_f[select], (row_f_new[select], col_f[select])), shape=(len(dID), nWords))
        else:
            Xevent = coo_matrix(
                (value_f, (row_f_new, col_f)), shape=(len(dID), nWords))
        Xevents.append(Xevent)
    return Xevents, dID


def csr_matrix2array(X):

    Xcoo = X.tocoo()
    Xrow = [int(v) for v in Xcoo.row]
    Xcol = [int(v) for v in Xcoo.col]
    Xval = [float(v) for v in Xcoo.data]

    return Xrow, Xcol, Xval


def array2csr_matrix(Xrow, Xcol, Xval, Xshape):

    recon = coo_matrix((Xval, (Xrow, Xcol)), shape=Xshape).tocsr()
    return recon


def saveX2session(X, session, name, start_str, end_str):
    Xrow, Xcol, Xval = csr_matrix2array(X)
    session[prepend_date(start_str, end_str, name + 'row')] = Xrow
    session[prepend_date(start_str, end_str, name + 'Xcol')] = Xcol
    session[prepend_date(start_str, end_str, name + 'Xval')] = Xval
    session[prepend_date(start_str, end_str, name + 'Xshape')] = X.shape

    return 'success'

def filterEvent(Pw_zs, Pz_d, Pd, mu, sigma):
    # eventID = Pz_d[:-1,:].dot(Pd).argsort()[::-1]

    # for i in xrange(len(eventID)):
    #     print "event ", eventID[i], "Pz is ", Pz_d[:-1,:].dot(Pd)[eventID[i]]
    # cluster_num = Pz_d.shape[0]-1
    # for i xrange(cluster_num):
    eventID = np.sort(Pw_zs[0][:,:-1],axis=0)[::-1,:][:10,:].sum(axis=0).argsort()[::-1] 
    topk = 35
    # input dID document metrics
    eventID = eventID[:topk]
    eventID = np.append(eventID, Pz_d.shape[0]-1)
    for i in xrange(len(Pw_zs)):
        Pw_zs[i] = Pw_zs[i][:,eventID]
    Pz_d = Pz_d[eventID,:]
    mu = mu[eventID]
    sigma = sigma[eventID]
    # print np.sort(np.sort(Pw_zs[0],axis=0)[::-1,:][:10,:].sum(axis=0))[::-1]

    return Pw_zs,Pz_d, mu, sigma, Pz_d.shape[0]-1


def filterEventKeyword(Pw_zs, Pz_d, Pd, mu, sigma, terms):
    # eventID = Pz_d[:-1,:].dot(Pd).argsort()[::-1]

    # for i in xrange(len(eventID)):
    #     print "event ", eventID[i], "Pz is ", Pz_d[:-1,:].dot(Pd)[eventID[i]]
    # cluster_num = Pz_d.shape[0]-1
    # for i xrange(cluster_num):
    cluster_num  = Pz_d.shape[0]-1
    sortedPw_z = np.argsort(Pw_zs[0][:,:-1],axis=0)[::-1,:][:10,:]
    eventID = np.zeros(2, dtype=np.int)
    for i in xrange(cluster_num):
        for j in xrange(10):
            if terms[sortedPw_z[j][i]].lower()== "apple":
                eventID[1] = i
                break
            if terms[sortedPw_z[j][i]].lower()== "squad":
                eventID[0] = i
                break
    eventID = np.append(eventID, Pz_d.shape[0]-1)

    for i in xrange(len(Pw_zs)):
        Pw_zs[i] = Pw_zs[i][:,eventID]
    Pz_d = Pz_d[eventID,:]
    mu = mu[eventID]
    sigma = sigma[eventID]
    # print np.sort(np.sort(Pw_zs[0],axis=0)[::-1,:][:10,:].sum(axis=0))[::-1]

    return Pw_zs,Pz_d, mu, sigma, eventID.size-1

def rankEventwithTime(Pw_zs,Pz_d,Pd, mu, sigma):
    eventID = mu[:-1].argsort()
    eventID = np.append(eventID, Pz_d.shape[0]-1)

    for i in xrange(len(Pw_zs)):
        Pw_zs[i] = Pw_zs[i][:,eventID]
    Pz_d = Pz_d[eventID,:]
    mu = mu[eventID]
    sigma = sigma[eventID]

    return Pw_zs,Pz_d, mu, sigma, Pz_d.shape[0]-1



