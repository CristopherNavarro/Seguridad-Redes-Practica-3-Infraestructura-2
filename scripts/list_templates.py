import urllib.request
import json

url = 'http://localhost:3080/v2/templates'
auth = 'Basic YWRtaW46VHNzRWtKSzc0M1pSOTdxNmt2Q25xc0kydVBBUUlvbURmTHBTNndiU3dsSkZwVEsxU1NNcVFvNVpSdlpuTEtpVA=='
req = urllib.request.Request(url, headers={'Authorization': auth})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    for t in data:
        print(f"{t['name']} | {t['template_id']} | {t['template_type']} | compute: {t.get('compute_id')}")
