# VKS Object Properties

Properties (non-numeric attributes) for each object type in the VKS object model, taken from the live APIs of a VCF 9.1 lab: vCenter REST API, Supervisor Kubernetes API v1.32, and VKS cluster Kubernetes API v1.35 (VKS 3.6, Cluster API `v1beta2`). Each property names the API field it comes from, so it can be checked against the manual.

Numeric attributes (counts, capacity, usage) are metrics and are listed in [metrics.md](metrics.md). The raw field-name lists these properties were selected from are in [raw/](raw/).

**Source legend**

| Code | API |
|---|---|
| VC | vCenter REST API: `/api/vcenter/namespace-management/*`, `/api/vcenter/namespaces/*` |
| SUP | Supervisor Kubernetes API (port 6443). Login: `POST https://<supervisor>/wcp/login` with vCenter SSO credentials |
| K8S | Kubernetes API of the cluster the object lives in (VKS cluster, or the Supervisor for Supervisor-side objects) |
| Derived | Computed from other fields |

Conventions: `conditions[type=X]` means the `status` of the condition whose `type` is X (`True`, `False`, `Unknown`); the condition's `reason` and `message` are available alongside it. A label is written as `labels[<key>]`.

| Object Type | Property | Source | API field | Values / notes |
|---|---|---|---|---|
| Supervisor | Name | VC | `supervisors/summaries` → `info.name` | |
| Supervisor | Supervisor ID | VC | `supervisor` | UUID |
| Supervisor | vSphere Cluster | VC | `namespace-management/clusters` → `cluster`, `cluster_name` | MoRef and name |
| Supervisor | API Endpoint | VC | `info.APIEndpoint` | Also `clusters/{c}` → `api_server_cluster_endpoint`, `api_server_management_endpoint` |
| Supervisor | Config Status | VC | `info.config_status` | `CONFIGURING`, `RUNNING`, `REMOVING`, `ERROR` |
| Supervisor | Kubernetes Status | VC | `info.kubernetes_status` | `READY`, `WARNING`, `ERROR` |
| Supervisor | Kubernetes Version | VC | `software/clusters` → `current_version` | |
| Supervisor | Desired Kubernetes Version | VC | `software/clusters` → `desired_version` | Differs from current during an upgrade |
| Supervisor | Available Upgrade Versions | VC | `software/clusters` → `available_versions[]` | |
| Supervisor | Upgrade State | VC | `software/clusters` → `state` | |
| Supervisor | Conditions | VC | `clusters/{c}` → `conditions[].type`, `status`, `severity`, `reason` | |
| Supervisor | Control Plane Size | VC | `clusters/{c}` → `size_hint` | `TINY`, `SMALL`, `MEDIUM`, `LARGE` |
| Supervisor | Network Provider | VC | `clusters/{c}` → `network_provider` | `NSX_VPC`, `NSXT_CONTAINER_PLUGIN`, `VSPHERE_NETWORK` |
| Supervisor | NSX Project | VC | `clusters/{c}` → `vpc_network.nsx_project` | NSX VPC only |
| Supervisor | VPC Connectivity Profile | VC | `clusters/{c}` → `vpc_network.vpc_connectivity_profile` | NSX VPC only |
| Supervisor | Service CIDR | VC | `clusters/{c}` → `service_cidr.address` (+ `prefix`) | |
| Supervisor | Management Network | VC | `clusters/{c}` → `master_management_network.network`, `.mode` | |
| Supervisor | DNS Servers (control plane / workload) | VC | `clusters/{c}` → `master_DNS[]`, `worker_DNS[]` | |
| Supervisor | NTP Servers (control plane / workload) | VC | `clusters/{c}` → `master_NTP_servers[]`, `workload_ntp_servers[]` | |
| Supervisor | Control Plane Storage Policy | VC | `clusters/{c}` → `master_storage_policy` | |
| Supervisor | Ephemeral Storage Policy | VC | `clusters/{c}` → `ephemeral_storage_policy` | |
| Supervisor | Image Storage Policy | VC | `clusters/{c}` → `image_storage.storage_policy` | |
| Supervisor | Default Image Registry | VC | `clusters/{c}` → `default_image_registry.hostname` | |
| Supervisor | VKS Content Library | VC | `clusters/{c}` → `default_kubernetes_service_content_library` | |
| Supervisor | vSphere Pods Enabled | VC | `clusters/{c}` → `vsphere_pods_enabled` | true / false |
| Supervisor | Supervisor Services Enabled | VC | `clusters/{c}` → `supervisor_services_enabled` | true / false |
| Supervisor | Login Banner | VC | `clusters/{c}` → `login_banner` | |
| Supervisor | TLS Endpoint Certificate | VC | `clusters/{c}` → `tls_endpoint_certificate` | PEM; expiry can be derived |
| Supervisor Namespace | Name | VC | `namespaces/instances` → `namespace` | |
| Supervisor Namespace | Supervisor | VC | `namespaces/instances/v2/{ns}` → `supervisor` | Parent |
| Supervisor Namespace | Description | VC | `description` | |
| Supervisor Namespace | Config Status | VC | `config_status` | `CONFIGURING`, `RUNNING`, `REMOVING`, `ERROR` |
| Supervisor Namespace | Self-Service Namespace | VC | `self_service_namespace` | true / false |
| Supervisor Namespace | Creator | VC | `creator.subject`, `creator.domain` | |
| Supervisor Namespace | Access List | VC | `access_list[].subject`, `subject_type`, `domain`, `role` | Role: `OWNER`, `EDIT`, `VIEW` |
| Supervisor Namespace | Zones | VC | `zones[].zone`, `zones[].type` | |
| Supervisor Namespace | Network Provider | VC | `network_spec.network_provider` | |
| Supervisor Namespace | VPC | VC | `network_spec.vpc_network.vpc` | NSX VPC only |
| Supervisor Namespace | Private CIDRs | VC | `network_spec.vpc_network.vpc_config.private_cidrs[]` | |
| Supervisor Namespace | Networks | VC | `networks[]` | |
| Supervisor Namespace | Storage Policies | VC | `storage_specs[].policy` | |
| Supervisor Namespace | VM Classes | VC | `vm_service_spec.vm_classes[]` | |
| Supervisor Namespace | Content Libraries | VC | `content_libraries[]`, `vm_service_spec.content_libraries[]` | |
| Supervisor Namespace | Network Ready | SUP | Namespace `conditions[type=NamespaceNetworkReady]` | |
| Supervisor Namespace | Phase | SUP | Namespace `status.phase` | `Active`, `Terminating` |
| Supervisor Service | Service ID | VC | `supervisor-services` → `supervisor_service` | for example `tkg.vsphere.vmware.com` |
| Supervisor Service | Display Name | VC | `supervisor-services/{id}` → `display_name` | |
| Supervisor Service | Description | VC | `description` | |
| Supervisor Service | Current Version | VC | `current_version` | |
| Supervisor Service | Desired Version | VC | `desired_version` | Differs from current during an upgrade |
| Supervisor Service | Config Status | VC | `config_status` | `CONFIGURING`, `CONFIGURED`, `ERROR`, `REMOVING` |
| Supervisor Service | Status Messages | VC | `messages[].severity`, `type`, `details.default_message` | |
| Supervisor Service | Service Namespace | VC | `service_namespace` | `svc-*` namespace on the Supervisor |
| Supervisor Service | Catalog State | VC | `/api/vcenter/namespace-management/supervisor-services/{id}` → `state` | `ACTIVATED`, `DEACTIVATED` |
| Supervisor Service | Must Be Installed | VC | catalog → `must_be_installed` | true / false |
| K8s Cluster | Name | SUP | `Cluster` `metadata.name` | |
| K8s Cluster | Supervisor Namespace | SUP | `metadata.namespace` | Parent |
| K8s Cluster | UID | SUP | `metadata.uid` | |
| K8s Cluster | Creation Time | SUP | `metadata.creationTimestamp` | |
| K8s Cluster | Phase | SUP | `status.phase` | `Pending`, `Provisioning`, `Provisioned`, `Deleting`, `Failed` |
| K8s Cluster | Kubernetes Version (VKr) | SUP | `spec.topology.version` | for example `v1.35.5+vmware.1` |
| K8s Cluster | Kubernetes Release (TKR) | SUP | `labels[run.tanzu.vmware.com/tkr]` | |
| K8s Cluster | ClusterClass | SUP | `spec.topology.classRef.name`, `.namespace` | for example `builtin-generic-v3.6.0` |
| K8s Cluster | API Endpoint | SUP | `spec.controlPlaneEndpoint.host` (+ `.port`) | |
| K8s Cluster | Pod CIDRs | SUP | `spec.clusterNetwork.pods.cidrBlocks[]` | |
| K8s Cluster | Service CIDRs | SUP | `spec.clusterNetwork.services.cidrBlocks[]` | |
| K8s Cluster | Service Domain | SUP | `spec.clusterNetwork.serviceDomain` | |
| K8s Cluster | CNI | SUP | `spec.topology.variables[name=…].value.cniRef.name` | |
| K8s Cluster | Certificate Rotation Enabled | SUP | `spec.topology.variables[].value.certificateRotation.enabled` | true / false |
| K8s Cluster | VM Class | SUP | `spec.topology.variables[name=vmClass].value` | |
| K8s Cluster | Storage Class | SUP | `spec.topology.variables[name=storageClass].value` | |
| K8s Cluster | Node Pool Names | SUP | `spec.topology.workers.machineDeployments[].name` | |
| K8s Cluster | Cluster Autoscaler Add-on | SUP | `labels[addon.addons.kubernetes.vmware.com/cluster-autoscaler]` | |
| K8s Cluster | Control Plane Initialized | SUP | `status.initialization.controlPlaneInitialized` | true / false |
| K8s Cluster | Infrastructure Provisioned | SUP | `status.initialization.infrastructureProvisioned` | true / false |
| K8s Cluster | Failure Domains | SUP | `status.failureDomains[].name`, `.controlPlane` | Zones |
| K8s Cluster | Available | SUP | `conditions[type=Available]` | |
| K8s Cluster | Control Plane Available | SUP | `conditions[type=ControlPlaneAvailable]` | |
| K8s Cluster | Control Plane Initialized (condition) | SUP | `conditions[type=ControlPlaneInitialized]` | |
| K8s Cluster | Control Plane Machines Ready | SUP | `conditions[type=ControlPlaneMachinesReady]` | |
| K8s Cluster | Control Plane Machines Up-to-date | SUP | `conditions[type=ControlPlaneMachinesUpToDate]` | |
| K8s Cluster | Workers Available | SUP | `conditions[type=WorkersAvailable]` | |
| K8s Cluster | Worker Machines Ready | SUP | `conditions[type=WorkerMachinesReady]` | |
| K8s Cluster | Worker Machines Up-to-date | SUP | `conditions[type=WorkerMachinesUpToDate]` | |
| K8s Cluster | Infrastructure Ready | SUP | `conditions[type=InfrastructureReady]` | |
| K8s Cluster | Add-ons Reconciled | SUP | `conditions[type=AddonsReconciled]` | VKS-specific |
| K8s Cluster | System Checks Succeeded | SUP | `conditions[type=SystemChecksSucceeded]` | VKS-specific |
| K8s Cluster | Updates Available | SUP | `conditions[type=UpdatesAvailable]` | VKS-specific; reason `AlreadyUpToDate` when none |
| K8s Cluster | Remote Connection Probe | SUP | `conditions[type=RemoteConnectionProbe]` | Supervisor can reach the cluster API |
| K8s Cluster | Topology Reconciled | SUP | `conditions[type=TopologyReconciled]` | |
| K8s Cluster | Rolling Out / Scaling Up / Scaling Down | SUP | `conditions[type=RollingOut]`, `ScalingUp`, `ScalingDown` | |
| K8s Cluster | Remediating | SUP | `conditions[type=Remediating]` | |
| K8s Cluster | Paused / Deleting | SUP | `conditions[type=Paused]`, `Deleting` | |
| K8s Node Pool | Name | SUP | `Cluster` `spec.topology.workers.machineDeployments[].name` | The `MachineDeployment` name is generated from it |
| K8s Node Pool | Node Pool Class | SUP | `spec.topology.workers.machineDeployments[].class` | for example `node-pool` |
| K8s Node Pool | Cluster | SUP | `MachineDeployment` `spec.clusterName` | Parent |
| K8s Node Pool | Phase | SUP | `status.phase` | `ScalingUp`, `ScalingDown`, `Running`, `Failed`, `Unknown` |
| K8s Node Pool | Rollout Strategy | SUP | `spec.rollout.strategy.type` | `RollingUpdate`, `OnDelete` |
| K8s Node Pool | Available | SUP | `conditions[type=Available]` | |
| K8s Node Pool | Machines Ready | SUP | `conditions[type=MachinesReady]` | |
| K8s Node Pool | Machines Up-to-date | SUP | `conditions[type=MachinesUpToDate]` | |
| K8s Node Pool | Rolling Out / Scaling Up / Scaling Down | SUP | `conditions[type=RollingOut]`, `ScalingUp`, `ScalingDown` | |
| K8s Node Pool | Remediating | SUP | `conditions[type=Remediating]` | |
| K8s Node | Name | K8S | `Node` `metadata.name` | |
| K8s Node | Role | Derived | `labels[node-role.kubernetes.io/control-plane]`; Supervisor ESX host: `labels[node-role.kubernetes.io/agent]` | Control plane, worker, or ESX host (Supervisor) |
| K8s Node | Node Pool | K8S | `labels[vks.vmware.com/nodepool]` | VKS only |
| K8s Node | Zone | K8S | `labels[topology.kubernetes.io/zone]` | |
| K8s Node | ESX Host | K8S | `labels[node.cluster.x-k8s.io/esxi-host]` | VKS only |
| K8s Node | Kubernetes Release (TKR) | K8S | `labels[run.tanzu.vmware.com/tkr]` | VKS only |
| K8s Node | Ready | K8S | `conditions[type=Ready]` | |
| K8s Node | Memory Pressure | K8S | `conditions[type=MemoryPressure]` | |
| K8s Node | Disk Pressure | K8S | `conditions[type=DiskPressure]` | |
| K8s Node | PID Pressure | K8S | `conditions[type=PIDPressure]` | |
| K8s Node | Machine Config Out of Date | K8S | `conditions[type=MachineConfigOutOfDate]` | VKS only |
| K8s Node | Schedulable | K8S | `spec.unschedulable` (absent = schedulable) | |
| K8s Node | Taints | K8S | `spec.taints[].key`, `.effect` | |
| K8s Node | Kubelet Version | K8S | `status.nodeInfo.kubeletVersion` | Supervisor ESX host shows a spherelet version (`-sph-`) |
| K8s Node | Kube-Proxy Version | K8S | `status.nodeInfo.kubeProxyVersion` | |
| K8s Node | Container Runtime Version | K8S | `status.nodeInfo.containerRuntimeVersion` | |
| K8s Node | OS Image | K8S | `status.nodeInfo.osImage` | Empty on Supervisor ESX host nodes |
| K8s Node | Operating System / Architecture | K8S | `status.nodeInfo.operatingSystem`, `.architecture` | |
| K8s Node | Kernel Version | K8S | `status.nodeInfo.kernelVersion` | |
| K8s Node | System UUID / Machine ID / Boot ID | K8S | `status.nodeInfo.systemUUID`, `.machineID`, `.bootID` | |
| K8s Node | Addresses | K8S | `status.addresses[].type`, `.address` | `InternalIP`, `ExternalIP`, `Hostname` |
| K8s Node | Pod CIDR | K8S | `spec.podCIDR`, `spec.podCIDRs[]` | VKS only |
| K8s Node | Provider ID | K8S | `spec.providerID` | `vsphere://<vm-uuid>`; links to the vCenter VM |
| K8s Node | Runtime Handlers | K8S | `status.runtimeHandlers[].name` | |
| K8s Node | Creation Time | K8S | `metadata.creationTimestamp` | |
| K8s Node | Machine Phase | SUP | `Machine` `status.phase` | `Pending`, `Provisioning`, `Provisioned`, `Running`, `Deleting`, `Failed` (VKS only) |
| K8s Node | Machine Health Conditions | SUP | `Machine` `conditions[type=…]`: `NodeHealthy`, `NodeReady`, `HealthCheckSucceeded`, `UpToDate`, `Updating` | VKS only |
| K8s Node | Control Plane Component Health | SUP | `Machine` `conditions[type=…]`: `APIServerPodHealthy`, `ControllerManagerPodHealthy`, `SchedulerPodHealthy`, `EtcdPodHealthy`, `EtcdMemberHealthy` | VKS control-plane nodes only |
| K8s Node | Certificates Expiry Date | SUP | `Machine` `status.certificatesExpiryDate` | VKS control-plane nodes only |
| K8s Node | Failure Domain | SUP | `Machine` `spec.failureDomain` | |
| K8s Node | VM Class | SUP | `VirtualMachine` `spec.className` | VKS only |
| K8s Node | VM Image | SUP | `VirtualMachine` `spec.imageName` | |
| K8s Node | Storage Class | SUP | `VirtualMachine` `spec.storageClass` | |
| K8s Node | vCenter VM ID | SUP | `VirtualMachine` `status.uniqueID` | for example `vm-12345` |
| K8s Node | VM Power State | SUP | `VirtualMachine` `status.powerState` | `PoweredOn`, `PoweredOff`, `Suspended` |
| K8s Node | Guest OS | SUP | `VirtualMachine` `status.guest.guestFullName` | |
| K8s Node | Primary IPv4 | SUP | `VirtualMachine` `status.network.primaryIP4` | |
| K8s Node | VM Zone | SUP | `VirtualMachine` `status.zone` | |
| K8s Namespace | Name | K8S | `Namespace` `metadata.name` | |
| K8s Namespace | Phase | K8S | `status.phase` | `Active`, `Terminating` |
| K8s Namespace | Creation Time | K8S | `metadata.creationTimestamp` | |
| K8s Namespace | System Namespace | Derived | name `kube-*`, `vmware-system-*`, `tkg-system`, `svc-*` | |
| K8s Workload | Name | K8S | `metadata.name` | |
| K8s Workload | Workload Type | Derived | Kind | `Deployment`, `StatefulSet`, `DaemonSet`, `ReplicaSet`, `Job`, `CronJob` |
| K8s Workload | Namespace | K8S | `metadata.namespace` | Parent |
| K8s Workload | Owner | K8S | `metadata.ownerReferences[].kind`, `.name` | ReplicaSet → Deployment, Job → CronJob |
| K8s Workload | Creation Time | K8S | `metadata.creationTimestamp` | |
| K8s Workload | Selector | K8S | `spec.selector.matchLabels` | |
| K8s Workload | Update Strategy | K8S | Deployment `spec.strategy.type`; StatefulSet, DaemonSet `spec.updateStrategy.type` | `RollingUpdate`, `Recreate`, `OnDelete` |
| K8s Workload | Available | K8S | Deployment `conditions[type=Available]` | |
| K8s Workload | Progressing | K8S | Deployment `conditions[type=Progressing]` | |
| K8s Workload | Pod Management Policy | K8S | StatefulSet `spec.podManagementPolicy` | `OrderedReady`, `Parallel` |
| K8s Workload | Service Name | K8S | StatefulSet `spec.serviceName` | |
| K8s Workload | PVC Retention Policy | K8S | StatefulSet `spec.persistentVolumeClaimRetentionPolicy.whenDeleted`, `.whenScaled` | |
| K8s Workload | Current / Update Revision | K8S | StatefulSet `status.currentRevision`, `status.updateRevision` | Differ during a rollout |
| K8s Workload | Complete / Failed | K8S | Job `conditions[type=Complete]`, `Failed`, `SuccessCriteriaMet` | |
| K8s Workload | Suspended | K8S | Job, CronJob `spec.suspend` | true / false |
| K8s Workload | Completion Mode | K8S | Job `spec.completionMode` | `NonIndexed`, `Indexed` |
| K8s Workload | Start / Completion Time | K8S | Job `status.startTime`, `status.completionTime` | |
| K8s Workload | Schedule | K8S | CronJob `spec.schedule` | Cron expression |
| K8s Workload | Concurrency Policy | K8S | CronJob `spec.concurrencyPolicy` | `Allow`, `Forbid`, `Replace` |
| K8s Workload | Last Schedule / Last Successful Time | K8S | CronJob `status.lastScheduleTime`, `status.lastSuccessfulTime` | |
| K8s Pod | Name | K8S | `Pod` `metadata.name` | |
| K8s Pod | Namespace | K8S | `metadata.namespace` | |
| K8s Pod | Owner (Workload) | K8S | `metadata.ownerReferences[].kind`, `.name` | |
| K8s Pod | Node | K8S | `spec.nodeName` | On the Supervisor, an ESX host for vSphere Pods |
| K8s Pod | Phase | K8S | `status.phase` | `Pending`, `Running`, `Succeeded`, `Failed`, `Unknown` |
| K8s Pod | Status Reason / Message | K8S | `status.reason`, `status.message` | for example `Evicted` |
| K8s Pod | Pod Scheduled | K8S | `conditions[type=PodScheduled]` | |
| K8s Pod | Initialized | K8S | `conditions[type=Initialized]` | |
| K8s Pod | Ready To Start Containers | K8S | `conditions[type=PodReadyToStartContainers]` | |
| K8s Pod | Containers Ready | K8S | `conditions[type=ContainersReady]` | |
| K8s Pod | Ready | K8S | `conditions[type=Ready]` | |
| K8s Pod | QoS Class | K8S | `status.qosClass` | `Guaranteed`, `Burstable`, `BestEffort` |
| K8s Pod | Pod IP | K8S | `status.podIP`, `status.podIPs[]` | |
| K8s Pod | Host IP | K8S | `status.hostIP`, `status.hostIPs[]` | |
| K8s Pod | Start Time | K8S | `status.startTime` | |
| K8s Pod | Creation Time | K8S | `metadata.creationTimestamp` | |
| K8s Pod | Restart Policy | K8S | `spec.restartPolicy` | `Always`, `OnFailure`, `Never` |
| K8s Pod | Priority Class | K8S | `spec.priorityClassName` | |
| K8s Pod | Service Account | K8S | `spec.serviceAccountName` | |
| K8s Pod | Host Network | K8S | `spec.hostNetwork` | true / false |
| K8s Pod | DNS Policy | K8S | `spec.dnsPolicy` | |
| K8s Pod | Scheduler | K8S | `spec.schedulerName` | |
| K8s Pod | Node Selector | K8S | `spec.nodeSelector` | |
| K8s Pod | vSphere Pod | Derived | Supervisor pod whose node is an ESX host (`node-role.kubernetes.io/agent`) | Supervisor only |
| K8s Container | Name | K8S | `spec.containers[].name` | |
| K8s Container | Pod | K8S | Parent pod | Parent |
| K8s Container | Container Type | Derived | `spec.containers[]` vs `spec.initContainers[]` | App or init |
| K8s Container | Image | K8S | `spec.containers[].image` | |
| K8s Container | Image ID | K8S | `status.containerStatuses[].imageID` | Digest |
| K8s Container | Image Pull Policy | K8S | `spec.containers[].imagePullPolicy` | `Always`, `IfNotPresent`, `Never` |
| K8s Container | Container ID | K8S | `status.containerStatuses[].containerID` | `containerd://…` |
| K8s Container | State | Derived | `status.containerStatuses[].state` key | `running`, `waiting`, `terminated` |
| K8s Container | State Reason | K8S | `state.waiting.reason`, `state.terminated.reason` | for example `CrashLoopBackOff`, `ImagePullBackOff`, `Completed`, `OOMKilled` |
| K8s Container | Started At | K8S | `state.running.startedAt` | |
| K8s Container | Ready | K8S | `status.containerStatuses[].ready` | true / false |
| K8s Container | Started | K8S | `status.containerStatuses[].started` | true / false |
| K8s Container | Last Termination Reason | K8S | `lastState.terminated.reason` | |
| K8s Container | Last Termination Message | K8S | `lastState.terminated.message` | |
| K8s Container | Last Termination Time | K8S | `lastState.terminated.startedAt`, `.finishedAt` | |
| K8s Container | Working Directory | K8S | `spec.containers[].workingDir` | |
| K8s Container | Termination Message Policy | K8S | `spec.containers[].terminationMessagePolicy` | |

## Notes for validating the manual

- **Cluster API version.** VKS 3.6 serves Cluster API `v1beta2`. Its condition names differ from `v1beta1` (for example `Available`, `ControlPlaneAvailable`, `WorkersAvailable`, `*MachinesUpToDate` replace `ControlPlaneReady` and `Ready`). The old names are still returned under `status.deprecated.v1beta1.conditions[]`.
- **VKS-specific cluster conditions.** `AddonsReconciled`, `SystemChecksSucceeded` and `UpdatesAvailable` are not part of upstream Cluster API.
- **Supervisor ESX host nodes** report a spherelet kubelet version, an empty OS image, and no ephemeral-storage or hugepages capacity.
- **Not seen in the lab.** Some fields only appear when set, so they did not appear in the lab but are part of the Kubernetes API schema: `spec.unschedulable`, Pod `status.reason` and `status.message`, `state.waiting.reason`, Job `Failed` condition, and container `lastState.terminated.message` on VKS (seen on the Supervisor).
