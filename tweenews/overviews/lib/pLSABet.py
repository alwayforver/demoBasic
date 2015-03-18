import numpy as np
from scipy.stats import norm
def getMatIndex(X):
    X = X.tocsr()
    indptr,indices = (X.indptr,X.indices)
    X = X.tocoo()
    docind,wordind,value = (X.row,X.col,X.data)
    if sum(indices-wordind)!=0:
        print "indices!=wordind"
        exit(0)
    return indptr,docind,wordind,value
def compute_Pw_d(wordind,docind,Pw_z,Pz_d):
    Pz_dw_ = Pw_z[wordind,:].T * Pz_d[:,docind]
    Pw_d = Pz_dw_.sum(axis=0)  # 1 x nnz
    return Pw_d, Pz_dw_
def compute_Pt_d(Pz_d,mu,sig,DT):
    K,nDocs = Pz_d.shape
    Pt_z=np.zeros((nDocs,K))
    for i in range(K):
        Pt_z[:,i] = norm.pdf(DT,loc=mu[i],scale=sig[i])
    Pt_z[Pt_z==0]=1e-7; # avoid numerical error
    Pz_dt_ = Pt_z.T*Pz_d # K x nDocs
    Pt_d = Pz_dt_.sum(axis=0) # 1 x nDocs
    return Pt_d, Pz_dt_
def EMstep(vitals,Pw_zs,Pz_d,forLis,lambdaB,wt,selectTime,timeData):
    K,nDocs = Pz_d.shape     
    Pz_d_out = np.zeros((K-1,nDocs))
    for i in range(len(vitals)):    
        indptr,docind,wordind,value = vitals[i]
        Pw_d, Pz_dw_ = forLis[i]
        Pw_z = Pw_zs[i]
        Pz_wd = Pz_dw_[:-1,:]/np.tile(Pw_d,(K-1,1))
        n_wdxPz_wd = np.tile(value,(K-1,1))*Pz_wd
        nWords = len(Pw_z)
        Pw_z_out = np.zeros((nWords,K-1))
        for indd in range(len(indptr)-1): # indd=i
            stInd = indptr[indd]
            enInd = indptr[indd+1]
            delta = n_wdxPz_wd[:,stInd:enInd]
            Pz_d_out[:,indd] += delta.sum(axis=1)
            indw = wordind[stInd:enInd]
            Pw_z_out[indw,:] += delta.T
        sumz = Pw_z_out.sum(axis=0)
        C = np.diag(1/sumz)
        Pw_z_out = np.dot(Pw_z_out, C)
        Pw_z = np.c_[Pw_z_out,Pw_z[:,-1]]
        Pw_zs[i] = Pw_z
    mu=[]
    sigma=[]
    if selectTime:
        DT,mu,sigma,forLit = timeData
        Pt_d, Pz_dt_ = forLit
        Pz_td = Pz_dt_[:-1,:]/np.tile(Pt_d,(K-1,1))
        weightsum = Pz_td.sum(axis=1)
        mu = np.append(np.dot(Pz_td,DT)/weightsum, mu[-1])
        for i in range(K-1):
            sigma[i] = np.sqrt( np.dot( Pz_td[i,:] , (DT-mu[i])**2 ) / weightsum[i] )
        Pz_d_out = Pz_d_out + wt*Pz_td
    sumd = Pz_d_out.sum(axis=0)
    Pz_d = np.vstack(( (1-lambdaB)*Pz_d_out/np.tile(sumd,(K-1,1)),Pz_d[-1,:] ))
    return Pw_zs,Pz_d,mu,sigma
def logL(vitals,Pd,forLis,forLit,wt):
    Li = []
    for i in range(len(vitals)):

        indptr,docind,wordind,value = vitals[i]
        Pw_d, Pz_dw_ = forLis[i]
    
        Li.append( (value*np.log(Pw_d * Pd[docind])).sum() )
    if forLit:
        Pt_d, Pz_dt_ = forLit
        Li.append( np.log(Pt_d*Pd).sum()*wt )        
    return sum(Li)
def pLSABet(selectTime,numX,Learn,data,inits,wt,lambdaB, debug = 0):
# data = [Xs,DT]
# inits = [Pz_d,Pw_z, Pp_z,Pl_z,Po_z,mu,sigma]        
    (Min_Likelihood_Change,Max_Iterations) = Learn
    Li=[]
    DT=[]
    mu=[]
    sigma=[]
    forLit=[]
    if selectTime:
        DT = data[-1]
        mu_B = np.mean(DT)
        sigma_B = np.std(DT)
        mu = np.append(inits[-2], mu_B)
        sigma = np.append(inits[-1], sigma_B)
        if (sigma==0).sum()>0:
            sigma[sigma==0] = 1e-7
            if debug == 1:
                print "zeros in sigma"        
    Xs = data[:numX]
    nDocs = Xs[0].shape[0]
# initializing...
    Pz_d = inits[0]
    Pz_d = np.vstack(( (1-lambdaB)*Pz_d,lambdaB*np.ones(nDocs) ))
    if selectTime:
#        Pt_d, Pz_dt_ = (Pz_d,mu,sig,DT)
        forLit = compute_Pt_d(Pz_d,mu,sigma,DT)

    Pw_zs = [] # inits[1:numX+1]
#    Pw_Bs = []
    vitals = []
    sumXs = 0 # for Pd
    sumXds = np.zeros(nDocs)
    forLis = []
    for i in range(numX):
        X = Xs[i]
        sumX = X.sum()
        sumXs += sumX
        sumXds += np.squeeze(np.asarray(X.sum(axis=1)))
        # background
        Pw_B = X.sum(axis=0)/sumX
        Pw_B = np.squeeze(np.asarray(Pw_B))
#        Pw_Bs.append(Pw_B)
        # init Pw_zs
        Pw_z = np.c_[inits[1+i],Pw_B]
        Pw_zs.append(Pw_z)
        # indices
        indptr,docind,wordind,value = getMatIndex(X)
        vitals.append( (indptr,docind,wordind,value) )
        # first time compute_Pw_d
        Pw_d, Pz_dw_ = compute_Pw_d(wordind,docind,Pw_z,Pz_d)
        forLis.append( (Pw_d, Pz_dw_) )
    if selectTime:
        Pd = (sumXds+wt)/(sumXs+wt*nDocs)
    else:
        Pd = sumXds/sumXs
# done inits
   # Pd_docind = Pd[docind] ####

    for it in range(Max_Iterations):
        if debug == 1:
            print "iteration: "+str(it)        
        Pw_zs,Pz_d,mu,sigma= EMstep(vitals,Pw_zs,Pz_d,forLis,lambdaB,wt,selectTime,(DT,mu,sigma,forLit))
        forLis = []
        for i in range(numX):
            _,docind,wordind,value = vitals[i]        
            Pw_d, Pz_dw_ = compute_Pw_d(wordind,docind,Pw_zs[i],Pz_d)
            forLis.append( (Pw_d, Pz_dw_) )
        if selectTime:
            forLit = compute_Pt_d(Pz_d,mu,sigma,DT) 
        Li.append(logL(vitals,Pd,forLis,forLit,wt))
        if it > 0:
            dLi = Li[it] - Li[it-1]
            if debug == 1:
                print "dLi = " + str(dLi)
            if dLi < Min_Likelihood_Change:
                break
    if debug == 1:
        print Li[-1]
    return Pw_zs,Pz_d,Pd,mu,sigma,Li

