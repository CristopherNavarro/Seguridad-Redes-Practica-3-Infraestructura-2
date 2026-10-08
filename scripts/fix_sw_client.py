import telnetlib
import time

HOST = "192.168.6.129"
PORT = 5002

def configure_sw_client():
    print("[*] Conectando a SW-Client (puerto 5002)...", flush=True)
    tn = telnetlib.Telnet(HOST, PORT, timeout=10)
    time.sleep(1)
    tn.write(b"\x03\r\n\r\n")
    time.sleep(1)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    print("Buffer inicial:", repr(buf[-100:]))
    
    if ">" in buf or "Switch>" in buf:
        tn.write(b"enable\r\n")
        time.sleep(1)
        
    tn.write(b"terminal length 0\r\n")
    time.sleep(0.5)
    tn.write(b"configure terminal\r\n")
    time.sleep(1)
    
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
        " no shutdown",
        "interface Gi0/1",
        " description ACCESS_PC_USER_NOPRIV",
        " switchport mode access",
        " switchport access vlan 10",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " no shutdown",
        "interface Gi0/2",
        " description ACCESS_PC_USER_PRIV",
        " switchport mode access",
        " switchport access vlan 10",
        " switchport nonegotiate",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " no shutdown",
        "interface range Gi0/3, Gi1/0 - 3, Gi2/0 - 3, Gi3/0 - 3",
        " switchport access vlan 999",
        " shutdown",
        "line con 0",
        " privilege level 15",
        " no login"
    ]
    
    for c in sw_cmds:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.08)
        
    tn.write(b"end\r\nwrite memory\r\n")
    time.sleep(3)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("[+] Salida de configuracion:\n", out[-500:])
    tn.close()

if __name__ == "__main__":
    configure_sw_client()
