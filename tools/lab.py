"""Read-only API clients for the VCF lab: V = vCenter REST, S = Supervisor K8s API, G = VKS cluster K8s API.

All lab values (hosts, user, password, VKS namespace/cluster) come from environment variables;
run tools/env.ps1 first, which loads them from the git-ignored .secrets/lab.env. Nothing is written to disk
except a client cert/key pair that is deleted immediately after loading.
"""
import os, json, ssl, base64, re, tempfile, urllib.request

VCENTER = os.environ["VC_HOST"]
SUPERVISOR = os.environ["SUP_HOST"]
USER = os.environ["VC_USER"]
VKS_NS, VKS_CLUSTER = os.environ["VKS_NS"], os.environ["VKS_CLUSTER"]
_ctx = ssl._create_unverified_context()
_basic = "Basic " + base64.b64encode(f"{USER}:{os.environ['VCPW']}".encode()).decode()


def leaves(o, p="", out=None, numeric_only=True):
    """Return the set of leaf field paths in a JSON object (values are discarded)."""
    out = set() if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            leaves(v, f"{p}.{k}" if p else k, out, numeric_only)
    elif isinstance(o, list):
        for v in o:
            leaves(v, p + "[]", out, numeric_only)
    elif not numeric_only or (isinstance(o, (int, float)) and not isinstance(o, bool)):
        out.add(p)
    return out


def mk(server, headers, ctx):
    def get(path):
        req = urllib.request.Request(server + path, headers=headers)
        try:
            return json.loads(urllib.request.urlopen(req, context=ctx, timeout=60).read())
        except urllib.error.HTTPError as e:
            return {"_err": e.code}
    return get


def _post(url):
    req = urllib.request.Request(url, method="POST", headers={"Authorization": _basic})
    return json.loads(urllib.request.urlopen(req, context=_ctx).read())


V = mk(f"https://{VCENTER}", {"vmware-api-session-id": _post(f"https://{VCENTER}/api/session")}, _ctx)
S = mk(f"https://{SUPERVISOR}:6443",
       {"Authorization": "Bearer " + _post(f"https://{SUPERVISOR}/wcp/login")["session_id"]}, _ctx)


def _guest():
    sec = S(f"/api/v1/namespaces/{VKS_NS}/secrets/{VKS_CLUSTER}-kubeconfig")
    if "_err" in sec:
        return None
    kc = base64.b64decode(sec["data"]["value"]).decode()
    g = lambda k: re.search(k + r":\s*(\S+)", kc).group(1)
    ctx = ssl._create_unverified_context()
    d = tempfile.mkdtemp()
    cf, kf = os.path.join(d, "c.crt"), os.path.join(d, "c.key")
    open(cf, "wb").write(base64.b64decode(g("client-certificate-data")))
    open(kf, "wb").write(base64.b64decode(g("client-key-data")))
    try:
        ctx.load_cert_chain(cf, kf)
    finally:
        os.remove(cf); os.remove(kf); os.rmdir(d)
    return mk(g("server"), {}, ctx)


G = _guest()  # None if the VKS cluster does not exist
