import urllib.request
import json
import time

PID = "ce838435-f3c3-41fe-bb9c-966821e828fd" # Seguridad_Redes_P3_Infraestructura_2
AUTH = "Basic YWRtaW46VHNzRWtKSzc0M1pSOTdxNmt2Q25xc0kydVBBUUlvbURmTHBTNndiU3dsSkZwVEsxU1NNcVFvNVpSdlpuTEtpVA=="
BASE_URL = "http://localhost:3080/v2"

TEMPLATES = {
    "fgt": "e569c93c-f57c-4a2b-affa-c9bf4d1cd6b8",
    "c7200": "0a9536ea-c2a5-4993-a954-3b077747a4ae",
    "iosvl2": "d877284d-a63d-41de-8d62-00bebcc28798",
    "alpine": "3c492563-51c2-4e7e-b466-bea9253585c6",
}

def req(url, method="GET", data=None):
    h = {"Authorization": AUTH, "Content-Type": "application/json"}
    d = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=d, headers=h, method=method)
    with urllib.request.urlopen(r) as resp:
        if resp.status == 204:
            return None
        return json.loads(resp.read().decode())

def create_template_node(template_id, name, x, y):
    print(f"Creando nodo '{name}'...")
    url = f"{BASE_URL}/projects/{PID}/templates/{template_id}"
    data = {"name": name, "x": x, "y": y}
    return req(url, method="POST", data=data)

def create_nat_node(name, x, y):
    print(f"Creando nodo NAT '{name}'...")
    url = f"{BASE_URL}/projects/{PID}/nodes"
    data = {
        "name": name,
        "node_type": "nat",
        "compute_id": "vm",
        "x": x,
        "y": y
    }
    return req(url, method="POST", data=data)

def main():
    print("Iniciando despliegue de nodos faltantes para Infraestructura 2...")
    
    # Obtener nodos ya creados
    existing_nodes = req(f"{BASE_URL}/projects/{PID}/nodes")
    existing_names = {n["name"] for n in existing_nodes}
    
    if "ISP-Router" not in existing_names:
        create_template_node(TEMPLATES["c7200"], "ISP-Router", 0, -200)
    if "Cisco-Edge-01" not in existing_names:
        create_template_node(TEMPLATES["c7200"], "Cisco-Edge-01", -300, -50)
    if "SW-Client" not in existing_names:
        create_template_node(TEMPLATES["iosvl2"], "SW-Client", -300, 100)
    if "PC-User-NoPriv" not in existing_names:
        create_template_node(TEMPLATES["alpine"], "PC-User-NoPriv", -420, 250)
    if "PC-User-Priv" not in existing_names:
        create_template_node(TEMPLATES["alpine"], "PC-User-Priv", -180, 250)
    if "FGT-Edge-02" not in existing_names:
        create_template_node(TEMPLATES["fgt"], "FGT-Edge-02", 200, -50)
    if "Srv-JumpServer" not in existing_names:
        create_template_node(TEMPLATES["alpine"], "Srv-JumpServer", 380, 100)
    if "Srv-Web-Caja" not in existing_names:
        create_template_node(TEMPLATES["alpine"], "Srv-Web-Caja", 200, 250)
    if "NAT1" not in existing_names:
        create_nat_node("NAT1", 380, -200)
        
    print("\nTodos los nodos existen. Leyendo mapeo de puertos...")
    nodes = req(f"{BASE_URL}/projects/{PID}/nodes")
    node_map = {n["name"]: n for n in nodes}
    
    def get_port(node_name, adapter_number=0, port_number=0):
        n = node_map[node_name]
        for p in n["ports"]:
            if p["adapter_number"] == adapter_number and p["port_number"] == port_number:
                return n["node_id"], p["adapter_number"], p["port_number"]
        for p in n["ports"]:
            if p["adapter_number"] == adapter_number:
                return n["node_id"], p["adapter_number"], p["port_number"]
        raise Exception(f"Puerto no encontrado en {node_name} (adapter {adapter_number}, port {port_number})")

    def add_link(n1_name, a1, p1, n2_name, a2, p2):
        id1, ad1, pt1 = get_port(n1_name, a1, p1)
        id2, ad2, pt2 = get_port(n2_name, a2, p2)
        link_data = {
            "nodes": [
                {"node_id": id1, "adapter_number": ad1, "port_number": pt1},
                {"node_id": id2, "adapter_number": ad2, "port_number": pt2}
            ]
        }
        print(f"Cableando {n1_name} (a{ad1}p{pt1}) <---> {n2_name} (a{ad2}p{pt2})...")
        return req(f"{BASE_URL}/projects/{PID}/links", method="POST", data=link_data)

    # Revisar enlaces existentes
    existing_links = req(f"{BASE_URL}/projects/{PID}/links")
    if not existing_links:
        # 1. ISP Fa0/0 <-> Cisco-Edge-01 Fa0/0
        add_link("ISP-Router", 0, 0, "Cisco-Edge-01", 0, 0)
        
        # 2. ISP Fa0/1 <-> FGT-Edge-02 adapter 0 (port1)
        add_link("ISP-Router", 0, 1, "FGT-Edge-02", 0, 0)
        
        # 3. Cisco-Edge-01 Fa1/0 <-> SW-Client Gi0/0 (trunk/access)
        add_link("Cisco-Edge-01", 1, 0, "SW-Client", 0, 0)
        
        # 4. SW-Client Gi0/1 <-> PC-User-NoPriv eth0
        add_link("SW-Client", 0, 1, "PC-User-NoPriv", 0, 0)
        
        # 5. SW-Client Gi0/2 <-> PC-User-Priv eth0
        add_link("SW-Client", 0, 2, "PC-User-Priv", 0, 0)
        
        # 6. FGT-Edge-02 adapter 1 (port2) <-> Srv-JumpServer eth0
        add_link("FGT-Edge-02", 1, 0, "Srv-JumpServer", 0, 0)
        
        # 7. FGT-Edge-02 adapter 2 (port3) <-> Srv-Web-Caja eth0
        add_link("FGT-Edge-02", 2, 0, "Srv-Web-Caja", 0, 0)
        
        # 8. FGT-Edge-02 adapter 3 (port4) <-> NAT1 nat0
        add_link("FGT-Edge-02", 3, 0, "NAT1", 0, 0)
    else:
        print(f"Ya existen {len(existing_links)} enlaces en el proyecto.")

    print("\n¡Topología de Infraestructura 2 completamente configurada y cableada!")

if __name__ == "__main__":
    main()
