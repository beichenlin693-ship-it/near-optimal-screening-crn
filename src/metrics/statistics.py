"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import math
import numpy as np
from scipy.stats import norm,t,beta
def wilson(k,n):
    assert n>0 and 0<=k<=n
    p=k/n;z=norm.ppf(.975);d=1+z*z/n;c=(p+z*z/(2*n))/d;r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (0. if k==0 else max(0.,c-r)),(1. if k==n else min(1.,c+r))
def cp(k,n):return (0. if k==0 else float(beta.ppf(.025,k,n-k+1)),1. if k==n else float(beta.ppf(.975,k+1,n-k)),1. if k==n else float(beta.ppf(.95,k+1,n-k)))
def moments(x):
    x=np.asarray(x,dtype=float);n=len(x);mean=float(x.mean());sd=float(x.std(ddof=1)) if n>1 else 0.;se=sd/math.sqrt(n);r=float(t.ppf(.975,n-1))*se if n>1 else 0.
    return dict(mean=mean,sd=sd,mcse=se,ci_low=mean-r,ci_high=mean+r,median=float(np.median(x)),p90=float(np.quantile(x,.9)),p95=float(np.quantile(x,.95)))
def proportion_difference(k1,n1,k0,n0):
    p1=k1/n1;p0=k0/n0;l1,u1=wilson(k1,n1);l0,u0=wilson(k0,n0);d=p1-p0
    return d,d-math.sqrt((p1-l1)**2+(u0-p0)**2),d+math.sqrt((u1-p1)**2+(p0-l0)**2)
def mean_difference(x,y):
    x=np.asarray(x);y=np.asarray(y);a=float(np.var(x,ddof=1))/len(x);b=float(np.var(y,ddof=1))/len(y);d=float(x.mean()-y.mean());se=math.sqrt(a+b)
    if se==0:return d,d,d
    df=(a+b)**2/(a*a/(len(x)-1)+b*b/(len(y)-1));r=float(t.ppf(.975,df))*se
    return d,d-r,d+r
def stable_rank(means,ids):return sorted(range(len(ids)),key=lambda j:(-float(means[j]),ids[j]))
def bootstrap_matrix(matrix,replicates,rng):
    n=len(matrix);out=np.empty((replicates,matrix.shape[1]))
    for b in range(replicates):out[b]=matrix[rng.integers(0,n,size=n)].mean(axis=0)
    return out
