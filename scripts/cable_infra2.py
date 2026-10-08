import urllib.request
import json

PID = "ce838435-f3c3-41fe-bb9c-966821e828fd"
AUTH = "Basic YWRtaW46VHNzRWtKSzc0M1pSOTdxNmt2Q25xc0kydVBBUUlvbURmTHBTNndiU3dsSkZwVEsxU1NNcVFvNVpSdlpuTEtpVA=="
BASE_URL = "http://localhost:3080/v2"

def req(url, method="GET", data=None):
    h = {"Authorization": AUTH, "Content-Type": "application/json"}
    d = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=d, headers=h, method=method)
    with urllib.request.urlopen(r) as resp:
        if resp.status == 204:
            return None
        return json.loads(resp.read().decode())

def main():
    nodes = req(f"{BASE_URL}/projects/{PID}/nodes")
    node_map = {n["name"]: n for n in nodes}

    def get_port(node_name, port_name=None, adapter_number=None, port_number=None):
        n = node_map[node_name]
        if port_name:
            for p in n["ports"]:
                if p["name"].lower() == port_name.lower():
                    return n["node_id"], p["adapter_number"], p["port_number"]
        if adapter_number is not None and port_number is not None:
            for p in n["ports"]:
                if p["adapter_number"] == adapter_number and p["port_number"] == port_number:
                    return n["node_id"], p["adapter_number"], p["port_number"]
        raise Exception(f"Port not found on {node_name}: {port_name or (adapter_number, port_number)}")

    def add_link(n1, p1_kwargs, n2, p2_kwargs):
        id1, a1, pt1 = get_port(n1, **p1_kwargs)
        id2, a2, pt2 = get_port(n2, **p2_kwargs)
        link_data = {
            "nodes": [
                {"node_id": id1, "adapter_number": a1, "port_number": pt1},
                {"node_id": id2, "adapter_number": a2, "port_number": pt2}
            ]
        }
        print(f"Cableando {n1} ({p1_kwargs}) <---> {n2} ({p2_kwargs})...")
        return req(f"{BASE_URL}/projects/{PID}/links", method="POST", data=link_data)

    existing_links = req(f"{BASE_URL}/projects/{PID}/links")
    print(f"Enlaces existentes: {len(existing_links)}")

    # 1. ISP Fa1/0 <-> FGT-Edge-02 port0 (FortiOS port1)
    add_link("ISP-Router", {"port_name": "FastEthernet1/0"}, "FGT-Edge-02", {"adapter_number": 0, "port_number": 0})

    # 2. Cisco-Edge-01 Fa1/0 <-> SW-Client Gi0/0
    add_link("Cisco-Edge-01", {"port_name": "FastEthernet1/0"}, "SW-Client", {"port_name": "Gi0/0"})

    # 3. SW-Client Gi0/1 <-> PC-User-NoPriv eth0
    add_link("SW-Client", {"port_name": "Gi0/1"}, "PC-User-NoPriv", {"adapter_number": 0, "port_number": 0})

    # 4. SW-Client Gi0/2 <-> PC-User-Priv eth0
    add_link("SW-Client", {"port_name": "Gi0/2"}, "PC-User-Priv", {"adapter_number": 0, "port_number": 0})

    # 5. FGT-Edge-02 adapter 1 (FortiOS port2) <-> Srv-JumpServer eth0
    add_link("FGT-Edge-02", {"adapter_number": 1, "port_number": 0}, "Srv-JumpServer", {"adapter_number": 0, "port_number": 0})

    # 6. FGT-Edge-02 adapter 2 (FortiOS port3) <-> Srv-Web-Caja eth0
    add_link("FGT-Edge-02", {"adapter_number": 2, "port_number": 0}, "Srv-Web-Caja", {"adapter_number": 0, "port_number": 0})

    # 7. FGT-Edge-02 adapter 3 (FortiOS port4) <-> NAT1 nat0
    add_link("FGT-Edge-02", {"adapter_number": 3, "port_number": 0}, "NAT1", {"adapter_number": 0, "port_number": 0})

    print("¡Todos los enlaces fueron creados exitosamente!")

if __name__ == "__main__":
    main()
