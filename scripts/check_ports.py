import urllib.request
import json

PID = 'ce838435-f3c3-41fe-bb9c-966821e828fd'
AUTH = 'Basic YWRtaW46VHNzRWtKSzc0M1pSOTdxNmt2Q25xc0kydVBBUUlvbURmTHBTNndiU3dsSkZwVEsxU1NNcVFvNVpSdlpuTEtpVA=='
h = {'Authorization': AUTH}
r = urllib.request.Request(f'http://localhost:3080/v2/projects/{PID}/nodes', headers=h)
nodes = json.loads(urllib.request.urlopen(r).read().decode())
for n in nodes:
    print(n['name'], ':')
    for p in n['ports']:
        print(f"  {p['name']} -> adapter {p['adapter_number']}, port {p['port_number']}")
