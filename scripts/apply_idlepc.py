import urllib.request
import json

PID = "ce838435-f3c3-41fe-bb9c-966821e828fd"
AUTH = "Basic YWRtaW46VHNzRWtKSzc0M1pSOTdxNmt2Q25xc0kydVBBUUlvbURmTHBTNndiU3dsSkZwVEsxU1NNcVFvNVpSdlpuTEtpVA=="
h = {"Authorization": AUTH, "Content-Type": "application/json"}
IDLEPC = "0x637e895c"

nodes = ["72a01842-cc49-4666-bbc6-ef06eac7e231", "c16d037e-d643-49c0-a2c2-a3c6e61755c1"]

for node_id in nodes:
    url = f"http://localhost:3080/v2/projects/{PID}/nodes/{node_id}"
    data = json.dumps({"properties": {"idlepc": IDLEPC}}).encode()
    r = urllib.request.Request(url, data=data, headers=h, method="PUT")
    res = json.loads(urllib.request.urlopen(r).read().decode())
    print(f"Updated {res['name']} idlepc: {res['properties'].get('idlepc')}")

tmpl_url = "http://localhost:3080/v2/templates/0a9536ea-c2a5-4993-a954-3b077747a4ae"
data_tmpl = json.dumps({"idlepc": IDLEPC}).encode()
r_tmpl = urllib.request.Request(tmpl_url, data=data_tmpl, headers=h, method="PUT")
res_tmpl = json.loads(urllib.request.urlopen(r_tmpl).read().decode())
print(f"Updated Cisco 7200 template idlepc: {res_tmpl.get('idlepc')}")
