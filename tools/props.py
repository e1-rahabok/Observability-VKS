# Property candidates: non-numeric field paths per object type -> ../raw/props_fields.json
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import leaves, V, S, G
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Collects NON-numeric field paths (property candidates) per object type. No values.
import os, sys, json, re

def items(get,p): b=get(p); return b if isinstance(b,list) else b.get("items",[]) if "_err" not in b else []
SKIP=re.compile(r"managedFields|annotations|resourceVersion|generation$|\.time$|lastHeartbeatTime|lastProbeTime|images\[\]|\.psi\.|ownerReferences\[\]\.(uid|blockOwnerDeletion|controller|apiVersion)|^apiVersion|^kind$|caBundle|volumes\[\]|env\[\]|volumeMounts|args\[\]|command\[\]|ports\[\]|probe|Probe|securityContext|tolerations|affinity|template\.|fieldRef|valueFrom|topologySpreadConstraints|labels\.[^\[]")
def P(objs):
    s=set()
    for o in objs: leaves(o,"",s,numeric_only=False)
    num=set()
    for o in objs: leaves(o,"",num,numeric_only=True)
    return sorted(x for x in s-num if not SKIP.search(x))
def labelkeys(objs): return sorted({k for o in objs for k in o.get("metadata",{}).get("labels",{})})
R={}
sup=items(V,"/api/vcenter/namespace-management/supervisors/summaries"); sid=sup[0]["supervisor"]
R["Supervisor | VC summaries"]=P(sup)
R["Supervisor | VC supervisor detail"]=P([V(f"/api/vcenter/namespace-management/supervisors/{sid}/summary")])
R["Supervisor | VC software/clusters"]=P(items(V,"/api/vcenter/namespace-management/software/clusters"))
R["Supervisor | VC clusters/{c}"]=P([V("/api/vcenter/namespace-management/clusters/"+items(V,"/api/vcenter/namespace-management/clusters")[0]["cluster"])])
nss=items(V,"/api/vcenter/namespaces/instances")
R["Supervisor Namespace | VC v2 detail"]=P([V("/api/vcenter/namespaces/instances/v2/"+n["namespace"]) for n in nss])
R["Supervisor Service | VC list"]=P(V(f"/api/vcenter/namespace-management/supervisors/{sid}/supervisor-services").get("supervisor_services",[]))
svcs=V(f"/api/vcenter/namespace-management/supervisors/{sid}/supervisor-services").get("supervisor_services",[])
R["Supervisor Service | VC detail"]=P([V(f"/api/vcenter/namespace-management/supervisors/{sid}/supervisor-services/{s['supervisor_service']}") for s in svcs])
R["Supervisor Service | VC catalog detail"]=P([V(f"/api/vcenter/namespace-management/supervisor-services/{s['supervisor_service']}") for s in svcs])
cl=items(S,"/apis/cluster.x-k8s.io/v1beta2/clusters")
R["K8s Cluster | SUP Cluster"]=P(cl); R["K8s Cluster | SUP Cluster labels"]=labelkeys(cl)
R["K8s Node Pool | SUP MachineDeployment"]=P(items(S,"/apis/cluster.x-k8s.io/v1beta2/machinedeployments"))
R["K8s Node | SUP Machine"]=P(items(S,"/apis/cluster.x-k8s.io/v1beta2/machines"))
R["K8s Node | SUP VirtualMachine"]=P(items(S,"/apis/vmoperator.vmware.com/v1alpha5/virtualmachines"))
for tag,get in (("VKS",G),("Supervisor",S)):
    n=items(get,"/api/v1/nodes"); R[f"K8s Node | {tag} Node"]=P(n); R[f"K8s Node | {tag} Node labels"]=labelkeys(n)
    R[f"K8s Namespace | {tag} Namespace"]=P(items(get,"/api/v1/namespaces"))
    p=items(get,"/api/v1/pods"); R[f"K8s Pod | {tag} Pod"]=P(p)
    for k,u in (("Deployment","/apis/apps/v1/deployments"),("StatefulSet","/apis/apps/v1/statefulsets"),("DaemonSet","/apis/apps/v1/daemonsets"),("ReplicaSet","/apis/apps/v1/replicasets"),("Job","/apis/batch/v1/jobs"),("CronJob","/apis/batch/v1/cronjobs")):
        R[f"K8s Workload | {tag} {k}"]=P(items(get,u))
json.dump(R,open("../raw/props_fields.json","w"),indent=1)
for k,v in R.items(): print(f"\n## {k} ({len(v)})\n  "+"\n  ".join(v))
