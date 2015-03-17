from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from time import time

import numpy as np
import sys,os

import pLSABet
import pickle

def inittime(DT,K,labels):
    mu = np.zeros(K)
    sigma = np.zeros(K)
    for i in range(K):
        ts = np.array(DT)[labels==i]
        mu[i] = np.mean(ts)
        sigma[i] = np.std(ts)
    return mu,sigma
                    

# input args: K display
with open('test30.pickle') as f:
    [X,Xp,Xl,Xo,X_all,K,Learn,Pz_d_km,Pw_z_km,Pw_z,Pz_d,Pd,Li,\
            labels,terms,termsp,termsl,termso,terms_all,DT,ind2obj,clusModel]=pickle.load(f)
if K!=int(sys.argv[1]):
    km = MiniBatchKMeans(n_clusters=k, init='k-means++', n_init=100,init_size=1000,
            batch_size=1000,verbose=True)
    km.fit(X)
    labels = km.labels_
    centers = km.cluster_centers_
    clus2doc = {}
    for i in range(len(labels)):
        clus2doc[labels[i]] = clus2doc.get(labels[i],set())
        clus2doc[labels[i]].add(i)    
## print number of docs in each cluster 
    for i in clus2doc:
        print (str(i+1)+"\t"+str(len(clus2doc[i])))

t0 = time()
Learn=(1,10)
selectTime = 1
numX = 1
#K=30
data = [X, DT]
mu_km, sigma_km= inittime(DT,K,labels)
inits = [Pz_d_km,Pw_z_km,mu_km,sigma_km]
wt = 0.5
lambdaB = 0.5
# data = [Xs,DT]
# inits = [Pz_d,Pw_z, Pp_z,Pl_z,Po_z,mu,sigma]        
Pw_zs,Pz_d,Pd,mu,sigma,Li = pLSABet.pLSABet(selectTime,numX,Learn,data,inits,wt,lambdaB)
print "pLSA done in "+str(time() - t0)

###################### split event###########################
def weightX(X,Pw_z,Pz_d):
    K = Pz_d.shape[0]
    X = X.tocoo()
    docind,wordind,value = (X.row,X.col,X.data)
    # Pz_do_f = Pz_do.*(Pz_do>(1-lambdaB)/double(K-1))
    Pz_d_f = Pz_d*(Pz_d>0.01)
    Pz_dw_ = Pw_z[wordind,:].T*Pz_d_f[:,docind]
    Pw_d = Pz_dw_.sum(axis=0) # 1 x nnz
    Pz_wd = Pz_dw_[:-1,:]/np.tile(Pw_d,(K-1,1))
    n_wdxPz_wd = np.tile(value,(K-1,1))*Pz_wd
    n_wdxPz_wd = n_wdxPz_wd *(n_wdxPz_wd>0.0001) ####
    return n_wdxPz_wd

n_wdxPz_wds = []
for i in range(numX):
    n_wdxPz_wds.append(  weightX(data[i],Pw_zs[i],Pz_d) )
from scipy.sparse import coo_matrix
# get event matrices
def selectTopic(Xs,n_wdxPz_wds,event):
    Xevents = []    
    for i in range(len(Xs)):
        X = Xs[i]
        n_wdxPz_wd = n_wdxPz_wds[i]
        nDocs,nWords=X.shape
        docind,wordind,value = (X.row,X.col,X.data)     
        value = n_wdxPz_wd[event,:]
        select = (value!=0)
        value_f = value[select]
        row_f = docind[select]  # 1 3 3 5 5 6 6 6 
        col_f = wordind[select]  
        if i==0:
            dID = np.unique(row_f) # 1 3 5 6
        dID2ind = -np.ones(nDocs) # -1 -1 -1 -1 -1 -1 -1 assume nDocs = 7
        dID2ind[dID] = np.arange(len(dID))  # 0 0 1 0 2 3 0
        row_f_new = dID2ind[row_f]  # 0 1 1 2 2 3 3 3
        if i>0:
            select = (col_f_new!=-1)
            Xevent = coo_matrix((value_f[select],(row_f_new[select],col_f[select])),shape=(len(dID),nWords))
        else:
            Xevent = coo_matrix((value_f,(row_f_new,col_f)),shape=(len(dID),nWords))
        Xevents.append(Xevent)        
    return Xevents,dID
###################### step 1 ###############
event = 0 # event number
Xevents,dID = selectTopic(data[:numX],n_wdxPz_wds,event)
DTevent = np.array(DT)[dID]
#data = Xevents+[DTevent] 
########################## event example ###############
Kevent=5
km = KMeans(n_clusters=Kevent, init='k-means++', max_iter=100, n_init=5)
km.fit(Xevents[0])
labels = km.labels_
centers = km.cluster_centers_

nDocs,nWords = Xevents[0].shape
Pz_d_km = np.zeros((Kevent,nDocs))
for i in range(nDocs):
    Pz_d_km[labels[i],i] = 1
Pz_d_km = Pz_d_km +0.01;
Pz_d_km = Pz_d_km / np.tile(sum(Pz_d_km),(Kevent,1))
C = centers.T+1/nWords/nWords
Pw_z_km = C/np.tile(sum(C),(nWords,1))

t0 = time()
Learn=(1,10)
selectTime = 1
numX = 1
#K=30
data = [Xevents[0], DTevent]
mu_km, sigma_km= inittime(DTevent,Kevent,labels)
inits = [Pz_d_km,Pw_z_km,mu_km,sigma_km]
wt = 0.1
lambdaB = 0.5
# data = [Xs,DT]
# inits = [Pz_d,Pw_z, Pp_z,Pl_z,Po_z,mu,sigma]        
Pw_zs,Pz_d,Pd,mu,sigma,Li = pLSABet.pLSABet(selectTime,numX,Learn,data,inits,wt,lambdaB)
print "pLSA done in "+str(time() - t0)
#################################################################################
# print topics
display = int(sys.argv[2])
if display == 1:
    M = 50
    N = 10
    wordInd = Pw_zs[0].argsort(axis=0)[::-1,:]
    docInd = Pz_d.argsort()[:,::-1]
    for i in range(Kevent): #
        sys.stdout.write("topic "+str(i))
        for j in range(M):
            sys.stdout.write('\t'+terms[wordInd[j,i]])
        sys.stdout.write('\n')
        for k in range(N):
            print(ind2obj[dID[docInd[i,k]]].title) #
