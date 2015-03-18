import time
from datetime import datetime, timedelta
from django.utils import timezone
import numpy as np
from scipy.sparse import csr_matrix, coo_matrix

def data_prep(news_list, ind2obj):
    raw_docs = []
    count = 0
    for each in news_list:
        raw_docs.append(each.title+' '+each.raw_text)
        ind2obj[count] = each
        count+=1
    return raw_docs

def parse_date(date_str):
    # in the form of 2015-01-01
    date_str = date_str[2:]
    if '-' in date_str:
        try:
            to_return = datetime.strptime(date_str, '%y-%m-%d')
        except:
            return None
    # in the form of 
    else:
        try:

            to_return = datetime.strptime(date_str, '%y%m%d')
        except:
            # print "wrong"
            return None

    return timezone.make_aware(to_return, timezone.get_default_timezone())

def prepend_date(start, end, to_write):
    return start+':'+end+':'+to_write

def find_toptitle_simple( Pz_d, ind2obj, top_n, cluster):
    ordered_ind = Pz_d.argsort(axis = 1)[:,::-1][:,:top_n]
    top_title = []

    for i in xrange(cluster):
        this = []
        for j in xrange(top_n):
            this.append(ind2obj[ ordered_ind[ i,j] ].title)
        top_title.append(this)
    return top_title

def find_topterms_simple(Pw_z, terms, top_n, cluster):
    ordered_ind = Pw_z.argsort(axis = 0)[::-1,:][:top_n,:]
    top_term = []

    for i in xrange(cluster):
        this = []
        for j in xrange(top_n):
            this.append(terms[   ordered_ind[ j , i]  ])
        top_term.append(this)
    return top_term

def parse_entity_str(entity_str):
    entities = entity_str.strip().split(';')
    result = {}
    result['place']={}
    result['org']={}
    result['person']={}
    for entity in entities:
        fields = entity.split(':')
        # print fields
        if len(fields)!=3:
            continue
        result[fields[1]][fields[0]] = int(fields[2])
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


        count[each_type]= 0
        voc[each_type] = {}
        mrow[each_type] =[]
        mcolumn[each_type] = []
        mvalue[each_type] =[]
        reverse_voc[each_type] = []

    cat_ent_cnt_list = []

    for entity_str in news_entities:
        cat_ent_cnt_list.append(parse_entity_str(entity_str)) 

    for cat_ent_cnt in cat_ent_cnt_list:
        for each_type in entityTypes:
            all_type_values = cat_ent_cnt[each_type].keys()
            # print all_type_values
            for type_value in all_type_values:
                if type_value not in voc[each_type]:
                    # print "haha"
                    voc[each_type][type_value] = count[each_type]
                    reverse_voc[each_type].append(type_value)
                    count[each_type]+=1



    # print len(voc['place']), voc['place']
    # print reverse_voc['place']

    doc_count = 0
    for cat_ent_cnt in cat_ent_cnt_list:
        for each_type in entityTypes:
            for ent, cnt in cat_ent_cnt[each_type].iteritems():
                mrow[each_type].append(doc_count)
                # print "haha", each_type
                # print ent, cnt
                mcolumn[each_type].append(voc[each_type][ent])
                mvalue[each_type].append(cnt)
        doc_count+=1


    for each_type in entityTypes:
        X[each_type] = coo_matrix( ( mvalue[each_type], (mrow[each_type],mcolumn[each_type]) ), shape= (doc_count, len(reverse_voc[each_type]) )).tocsr()


    # print X['place'], type(X['place'])

    # print cat_ent_cnt_list[505], reverse_voc['place'][60]
    return X, reverse_voc

def inittime(DT,K,labels):
    mu = np.zeros(K)
    sigma = np.zeros(K)
    for i in range(K):
        ts = np.array(DT)[labels==i]
        mu[i] = np.mean(ts)
        sigma[i] = np.std(ts)
    return mu,sigma

def get_ticks(exact_time):
    return (exact_time - timezone.make_aware(datetime(1970,1,1),timezone.get_default_timezone()) ).total_seconds()

