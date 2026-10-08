import urllib.request
import json

PID = 'ce838435-f3c3-41fe-bb9c-966821e828fd'
AUTH = 'Basic YWRtaW46VHNzRWtKSzc0M1pSOTdxNmt2Q25xc0kydVBBUUlvbURmTHBTNndiU3dsSkZwVEsxU1NNcVFvNVpSdlpuTEtpVA=='
h = {'Authorization': AUTH}
r = urllib.request.Request(f'http://localhost:3080/v2/projects/{PID}/nodes', headers=h)
nodes = json.loads(urllib.request.urlopen(r).read().decode())
for n in sorted(nodes, key=lambda x: x['name']):
    print(f"{n['name']:<18} | {n['node_type']:<10} | {n['status']:<8} | Console: {n.get('console')}")
