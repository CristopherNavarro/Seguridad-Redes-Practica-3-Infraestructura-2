import telnetlib
import time
import sys

HOST = "192.168.6.129"

def query_node(name, port, cmds, is_cisco=False, is_fgt=False):
    print(f"\n========================================================")
    print(f"AUDITORÍA EN VIVO: {name} (Puerto {port})")
    print(f"========================================================", flush=True)
    try:
        tn = telnetlib.Telnet(HOST, port, timeout=10)
        time.sleep(0.5)
        tn.write(b"\r\n")
        time.sleep(0.5)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        
        if is_fgt:
            if "login:" in buf:
                tn.write(b"admin\r\n")
                time.sleep(0.5)
            if "Password:" in buf:
                tn.write(b"Fortinet2025!\r\n")
                time.sleep(1)
            tn.write(b"config system console\r\nset output standard\r\nend\r\n")
            time.sleep(0.5)
            
        if is_cisco:
            if ">" in buf:
                tn.write(b"enable\r\n")
                time.sleep(0.5)
            tn.write(b"terminal length 0\r\n")
            time.sleep(0.5)
            
        out_total = ""
        for cmd in cmds:
            tn.write(cmd.encode('ascii') + b"\r\n" if not is_cisco and not is_fgt else cmd.encode('ascii') + b"\r\n")
            time.sleep(1.2)
            res = tn.read_very_eager().decode('ascii', errors='ignore')
            print(f">>> {cmd}\n{res.strip()}")
            out_total += f"\n>>> {cmd}\n{res.strip()}"
            
        tn.close()
        return out_total
    except Exception as e:
        print(f"[-] Error en {name}: {e}", flush=True)
        return str(e)

def main():
    # 1. ISP Router
    query_node("ISP-Router", 5000, [
        "show ip interface brief",
        "ping 200.25.7.2",
        "ping 200.25.7.6"
    ], is_cisco=True)

    # 2. Cisco Edge 01
    query_node("Cisco-Edge-01", 5001, [
        "show ip interface brief",
        "show ip route",
        "ping 200.25.7.6",
        "show crypto isakmp sa",
        "show crypto ipsec sa"
    ], is_cisco=True)

    # 3. FortiGate FGT-Edge-02
    query_node("FGT-Edge-02", 5008, [
        "get system status",
        "diagnose ip address list",
        "get router info routing-table all",
        "diagnose vpn ike gateway list",
        "diagnose vpn tunnel list",
        "show firewall policy"
    ], is_fgt=True)

    # 4. PC-User-NoPriv
    query_node("PC-User-NoPriv", 5004, [
        "ip addr show dev eth0",
        "ping -c 2 10.25.10.1",
        "curl -I --connect-timeout 3 http://10.25.30.2",
        "nc -zv -w 2 10.25.30.2 22",
        "nc -zv -w 2 10.25.20.2 80"
    ])

    # 5. PC-User-Priv
    query_node("PC-User-Priv", 5006, [
        "ip addr show dev eth0",
        "ping -c 2 10.25.10.1",
        "curl -I --connect-timeout 3 http://10.25.30.2",
        "nc -zv -w 2 10.25.30.2 22",
        "nc -zv -w 2 10.25.30.2 3389",
        "nc -zv -w 2 10.25.20.2 80"
    ])

    # 6. Srv-JumpServer
    query_node("Srv-JumpServer", 5010, [
        "ip addr show dev eth0",
        "ping -c 2 10.25.20.2",
        "nc -zv -w 2 10.25.20.2 443",
        "nc -zv -w 2 10.25.20.2 22",
        "nc -zv -w 2 10.25.20.2 3389",
        "curl -I --connect-timeout 2 http://10.25.20.2:80"
    ])

if __name__ == "__main__":
    main()
