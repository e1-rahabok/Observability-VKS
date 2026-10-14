# Metric candidates: numeric field paths per source -> ../raw/fields.json
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import leaves, V, S, G
os.chdir(os.path.dirname(os.path.abspath(__file__)))
R={}
def items(get,p): b=get(p); return b if isinstance(b,list) else b.get("items",[]) if "_err" not in b else [b]
def coll(key,objs,sub=None,numeric_only=True):
    s=set()
    for o in objs: leaves(o if sub is None else o.get(sub,{}), "", s, numeric_only)
    R[key]=sorted(s)
# --- vCenter
sup=items(V,"/api/vcenter/namespace-management/supervisors/summaries")
coll("vcenter: supervisor summary", sup, "info")
sid=sup[0]["supervisor"] if sup and "supervisor" in sup[0] else None
coll("vcenter: supervisor-services", items(V,f"/api/vcenter/namespace-management/supervisors/{sid}/supervisor-services") if sid else [], numeric_only=False)
nss=items(V,"/api/vcenter/namespaces/instances")
coll("vcenter: namespace v2 detail", [V("/api/vcenter/namespaces/instances/v2/"+n["namespace"]) for n in nss])
# --- Supervisor K8s access checks
nodes=items(S,"/api/v1/nodes")
R["supervisor: access"]=[f"metrics.k8s.io nodes -> {S('/apis/metrics.k8s.io/v1beta1/nodes').get('_err','200')}",
  f"kubelet stats/summary -> {S('/api/v1/nodes/'+nodes[0]['metadata']['name']+'/proxy/stats/summary').get('_err','200') if nodes else 'n/a'}"]
coll("supervisor: Cluster.status (CAPI)", items(S,"/apis/cluster.x-k8s.io/v1beta2/clusters"), "status")
coll("supervisor: Cluster.spec (CAPI)", items(S,"/apis/cluster.x-k8s.io/v1beta2/clusters"), "spec")
coll("supervisor: MachineDeployment.status", items(S,"/apis/cluster.x-k8s.io/v1beta2/machinedeployments"), "status")
coll("supervisor: KubeadmControlPlane.status", items(S,"/apis/controlplane.cluster.x-k8s.io/v1beta2/kubeadmcontrolplanes"), "status")
coll("supervisor: ZoneResourceUtilization", items(S,"/apis/topology.tanzu.vmware.com/v1alpha1/zoneresourceutilizations"))
coll("supervisor: StoragePolicyQuota", items(S,"/apis/cns.vmware.com/v1alpha2/storagepolicyquotas"), numeric_only=False)
coll("supervisor: StoragePolicyUsage", items(S,"/apis/cns.vmware.com/v1alpha2/storagepolicyusages"), numeric_only=False)
coll("supervisor: Node.status.capacity keys", items(S,"/api/v1/nodes"), "status")
# --- Guest cluster
gn=items(G,"/api/v1/nodes")
coll("guest: Node.status", gn, "status")
summ=[G(f"/api/v1/nodes/{n['metadata']['name']}/proxy/stats/summary") for n in gn]
coll("guest: kubelet summary .node", [s["node"] for s in summ])
coll("guest: kubelet summary .pods[]", [p for s in summ for p in s["pods"]])
coll("guest: kubelet summary .pods[].containers[]", [c for s in summ for p in s["pods"] for c in p.get("containers",[])])
coll("guest: metrics.k8s.io NodeMetrics", items(G,"/apis/metrics.k8s.io/v1beta1/nodes"), numeric_only=False)
coll("guest: metrics.k8s.io PodMetrics", items(G,"/apis/metrics.k8s.io/v1beta1/pods"), numeric_only=False)
pods=items(G,"/api/v1/pods")
coll("guest: Pod.status", pods, "status")
coll("guest: Pod.spec.containers[].resources", [c.get("resources",{}) for p in pods for c in p["spec"]["containers"]], numeric_only=False)
coll("guest: ResourceQuota", items(G,"/api/v1/resourcequotas"), "status", numeric_only=False)
for k,p in (("Deployment","/apis/apps/v1/deployments"),("StatefulSet","/apis/apps/v1/statefulsets"),("DaemonSet","/apis/apps/v1/daemonsets"),("ReplicaSet","/apis/apps/v1/replicasets"),("Job","/apis/batch/v1/jobs"),("CronJob","/apis/batch/v1/cronjobs")):
    coll(f"guest: {k}.status", items(G,p), "status")
json.dump(R,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","raw","fields.json"),"w"),indent=1)
for k,v in R.items(): print(f"\n## {k} ({len(v)})"); print("  "+"\n  ".join(v[:80]))
