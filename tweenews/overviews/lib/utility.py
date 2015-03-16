import time
from datetime import datetime, timedelta
from django.utils import timezone
import numpy


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

    # print "j",Pz_d


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