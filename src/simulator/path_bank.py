"""Inputs: explicit arguments described by function signatures.
Outputs: algorithm decisions, model objects or metrics; no work on import.
Runtime: depends on caller workload. This library is not a reproduction entrypoint.
Scientific rules are retained; only packaging imports and documentation are adapted.
"""
import hashlib,json
from collections import OrderedDict
DOMAINS={'calibration':1,'truth':2,'selection':3,'smoke':4,'variance_on':5,'variance_off':6,'benchmark':7,'toy':8,'variance_screen':9}

def path_key(domain,run_id,policy_id,index,crn):
    if domain not in DOMAINS or index<1:raise ValueError('Invalid bank or prefix index')
    return json.dumps([domain,run_id,'shared' if crn else policy_id,int(index)],separators=(',',':'))

def replication_id(path_id):
    domain=json.loads(path_id)[0]
    return (DOMAINS[domain]<<128)|int.from_bytes(hashlib.sha256(path_id.encode()).digest()[:16],'big')

class PathBank:
    def __init__(self,simulator,domain,run_id,crn,max_cached=256):
        self.simulator=simulator;self.domain=domain;self.run_id=run_id;self.crn=crn
        self.max_cached=max_cached;self.cache=OrderedDict()
    def key(self,policy,index):return path_key(self.domain,self.run_id,policy,index,self.crn)
    def get(self,path_id):
        if path_id not in self.cache:
            self.cache[path_id]=self.simulator.path(replication_id(path_id))
            if len(self.cache)>self.max_cached:self.cache.popitem(last=False)
        return self.cache[path_id]
