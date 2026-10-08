import telnetlib
import time
import sys

HOST = "192.168.6.129"

def send_cisco_cmds(name, port, cmds):
    print(f"[*] Configurando {name} (puerto {port})...", flush=True)
    try:
        tn = telnetlib.Telnet(HOST, port, timeout=10)
        time.sleep(1)
        tn.write(b"\r\n\r\n")
        time.sleep(1)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        
        if ">" in buf:
            tn.write(b"enable\r\n")
            time.sleep(1)
            
        tn.write(b"terminal length 0\r\n")
        time.sleep(0.5)
        tn.write(b"configure terminal\r\n")
        time.sleep(0.5)
        
        for c in cmds:
            tn.write(c.encode('ascii') + b"\r\n")
            time.sleep(0.1)
            
        tn.write(b"end\r\n")
        time.sleep(1)
        tn.write(b"write memory\r\n")
        time.sleep(3)
        out = tn.read_very_eager().decode('ascii', errors='ignore')
        tn.close()
        print(f"[+] {name} configurado exitosamente.", flush=True)
        return True, out
    except Exception as e:
        print(f"[-] Error configurando {name}: {e}", flush=True)
        return False, str(e)

def main():
    # 1. ISP-Router
    isp_cmds = [
        "hostname ISP-Router",
        "no ip domain-lookup",
        "interface FastEthernet0/0",
        " description WAN_TO_CISCO_EDGE",
        " ip address 200.25.7.1 255.255.255.252",
        " no shutdown",
        "interface FastEthernet1/0",
        " description WAN_TO_FORTIGATE_PORT1",
        " ip address 200.25.7.5 255.255.255.252",
        " no shutdown",
        "line con 0",
        " privilege level 15",
        " no login",
        " logging synchronous"
    ]
    send_cisco_cmds("ISP-Router", 5000, isp_cmds)

    # 2. Cisco-Edge-01
    cisco_edge_cmds = [
        "hostname Cisco-Edge-01",
        "no ip domain-lookup",
        "interface FastEthernet0/0",
        " description WAN_TO_ISP",
        " ip address 200.25.7.2 255.255.255.252",
        " no shutdown",
        "ip route 0.0.0.0 0.0.0.0 200.25.7.1",
        "interface FastEthernet1/0",
        " no shutdown",
        "interface FastEthernet1/0.10",
        " description LAN_VLAN10_USERS",
        " encapsulation dot1Q 10",
        " ip address 10.25.10.1 255.255.255.128",
        "ip dhcp excluded-address 10.25.10.1 10.25.10.9",
        "ip dhcp pool VLAN10_USERS",
        " network 10.25.10.0 255.255.255.128",
        " default-router 10.25.10.1",
        " dns-server 8.8.8.8",
        "exit",
        # IPsec VPN
        "crypto isakmp policy 10",
        " encr aes 256",
        " hash sha256",
        " authentication pre-share",
        " group 14",
        " lifetime 86400",
        "exit",
        "crypto isakmp key ITLA2025! address 200.25.7.6",
        "crypto ipsec transform-set TSET esp-aes 256 esp-sha256-hmac",
        " mode tunnel",
        "exit",
        "ip access-list extended VPN_TRAFFIC",
        " permit ip 10.25.10.0 0.0.0.127 10.25.30.0 0.0.0.7",
        "exit",
        "crypto map CMAP 10 ipsec-isakmp",
        " set peer 200.25.7.6",
        " set transform-set TSET",
        " match address VPN_TRAFFIC",
        "exit",
        "interface FastEthernet0/0",
        " crypto map CMAP",
        "exit",
        "line con 0",
        " privilege level 15",
        " no login",
        " logging synchronous"
    ]
    send_cisco_cmds("Cisco-Edge-01", 5001, cisco_edge_cmds)

    # 3. SW-Client (Cisco IOSvL2)
    sw_cmds = [
        "hostname SW-Client",
        "no ip domain-lookup",
        "vlan 10",
        " name VLAN10_USERS",
        "vlan 99",
        " name NATIVE_MGMT",
        "vlan 999",
        " name BLACKHOLE_UNUSED",
        "interface Gi0/0",
        " description TRUNK_TO_ROUTER",
        " switchport trunk encapsulation dot1q",
        " switchport mode trunk",
        " switchport trunk native vlan 99",
        " switchport trunk allowed vlan 10",
        " negotiation auto",
        "interface Gi0/1",
        " description ACCESS_PC_USER_NOPRIV",
        " switchport mode access",
        " switchport access vlan 10",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        "interface Gi0/2",
        " description ACCESS_PC_USER_PRIV",
        " switchport mode access",
        " switchport access vlan 10",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        "interface range Gi0/3, Gi1/0 - 3, Gi2/0 - 3, Gi3/0 - 3",
        " switchport access vlan 999",
        " shutdown",
        "line con 0",
        " privilege level 15",
        " no login"
    ]
    send_cisco_cmds("SW-Client", 5002, sw_cmds)

if __name__ == "__main__":
    main()
