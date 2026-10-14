# Metric gaps: Supervisor kubelet stats, capacity keys, StatefulSet/Job/CronJob -> ../raw/fields2.json
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import leaves, V, S, G
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import os, sys, json

R2={}
def items(get,p): b=get(p); return b.get("items",[]) if isinstance(b,dict) and "_err" not in b else b
def keys(objs, path):
    s=set()
    for o in objs:
        x=o
        for k in path.split("."): x=(x or {}).get(k,{})
        s|=set(x.keys()) if isinstance(x,dict) else set()
    return sorted(s)
sn=items(S,"/api/v1/nodes")
for kind in ("control-plane VM","ESX host (spherelet)"):
    ns=[n for n in sn if ("node-role.kubernetes.io/control-plane" in n["metadata"]["labels"])==(kind=="control-plane VM")]
    summ=[S(f"/api/v1/nodes/{n['metadata']['name']}/proxy/stats/summary") for n in ns]
    R2[f"sup kubelet summary node [{kind}]"]=sorted(leaves([s.get("node",{}) for s in summ]))
    R2[f"sup kubelet summary pods[] [{kind}]"]=sorted({x for s in summ for p in s.get("pods",[]) for x in leaves({k:v for k,v in p.items() if k!="containers"})})
    R2[f"sup kubelet summary containers[] [{kind}]"]=sorted({x for s in summ for p in s.get("pods",[]) for c in p.get("containers",[]) for x in leaves(c)})
    R2[f"sup Node capacity keys [{kind}]"]=keys(ns,"status.capacity"); R2[f"sup Node allocatable keys [{kind}]"]=keys(ns,"status.allocatable")
gn=items(G,"/api/v1/nodes")
R2["guest Node capacity keys"]=keys(gn,"status.capacity"); R2["guest Node allocatable keys"]=keys(gn,"status.allocatable")
R2["guest Node condition types"]=sorted({c["type"] for n in gn for c in n["status"]["conditions"]})
for k,p in (("StatefulSet","/apis/apps/v1/statefulsets"),("Job","/apis/batch/v1/jobs"),("CronJob","/apis/batch/v1/cronjobs")):
    R2[f"sup {k}.status (numeric)"]=sorted(leaves([o.get("status",{}) for o in items(S,p)]))
    R2[f"sup {k}.status (all)"]=sorted(leaves([o.get("status",{}) for o in items(S,p)],numeric_only=False))
rq=items(G,"/api/v1/resourcequotas")
R2["guest ResourceQuota status.hard keys"]=keys(rq,"status.hard"); R2["guest ResourceQuota status.used keys"]=keys(rq,"status.used"); R2["guest ResourceQuota spec.hard keys"]=keys(rq,"spec.hard")
for v in ("v1alpha1",):
    b=S(f"/apis/topology.tanzu.vmware.com/{v}/zoneresourceutilizations"); R2["sup ZoneResourceUtilization err"]=[str(b.get("_err",""))]
    b2=S(f"/apis/topology.tanzu.vmware.com/v1alpha1/namespaces/{os.environ['VKS_NS']}/zoneresourceutilizations"); R2["sup ZoneResourceUtilization (namespaced) fields"]=sorted(leaves(b2.get("items",[]),numeric_only=False)) if "_err" not in b2 else [str(b2)]
gp=items(G,"/api/v1/pods")
R2["guest Pod phases/condition types"]=sorted({c["type"] for p in gp for c in p["status"].get("conditions",[])})
json.dump(R2,open("../raw/fields2.json","w"),indent=1)
for k,v in R2.items(): print(f"\n## {k} ({len(v)})\n  "+"\n  ".join(x for x in v if ".psi." not in x))
