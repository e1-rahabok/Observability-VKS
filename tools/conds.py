# Condition types and phases per object kind (printed)
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import leaves, V, S, G
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def items(get,p): b=get(p); return b.get("items",[]) if "_err" not in b else []
for name,get,p in (("Cluster",S,"/apis/cluster.x-k8s.io/v1beta2/clusters"),("MachineDeployment",S,"/apis/cluster.x-k8s.io/v1beta2/machinedeployments"),("Machine",S,"/apis/cluster.x-k8s.io/v1beta2/machines"),("VirtualMachine",S,"/apis/vmoperator.vmware.com/v1alpha5/virtualmachines"),("Node VKS",G,"/api/v1/nodes"),("Node SUP",S,"/api/v1/nodes"),("Namespace SUP",S,"/api/v1/namespaces"),("Deployment",S,"/apis/apps/v1/deployments"),("Job",S,"/apis/batch/v1/jobs"),("Pod SUP",S,"/api/v1/pods")):
    o=items(get,p); print(name, sorted({c["type"] for x in o for c in x.get("status",{}).get("conditions",[])}), "phases", sorted({str(x.get("status",{}).get("phase")) for x in o}))
