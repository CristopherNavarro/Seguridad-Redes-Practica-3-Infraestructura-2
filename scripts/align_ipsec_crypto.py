import telnetlib
import time

HOST = "192.168.6.129"

def align_cisco():
    print("[*] Alineando IPsec en Cisco-Edge-01...")
    tn = telnetlib.Telnet(HOST, 5001, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nenable\r\nterminal length 0\r\nconfigure terminal\r\n")
    time.sleep(0.5)
    
    cmds = [
        "no crypto isakmp policy 10",
        "crypto isakmp policy 10",
        " encr aes 256",
        " hash sha",
        " authentication pre-share",
        " group 14",
        " lifetime 86400",
        "exit",
        "crypto isakmp key ITLA2025! address 200.25.7.6",
        "crypto ipsec transform-set TSET esp-aes 256 esp-sha-hmac",
        " mode tunnel",
        "exit",
        "crypto map CMAP 10 ipsec-isakmp",
        " set peer 200.25.7.6",
        " set transform-set TSET",
        " match address VPN_TRAFFIC",
        "exit",
        "interface FastEthernet0/0",
        " crypto map CMAP",
        "exit",
        "end",
        "write memory"
    ]
    for c in cmds:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.1)
    time.sleep(2)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("[+] Cisco-Edge-01 configurado.")
    tn.close()

def align_fgt():
    print("[*] Alineando IPsec en FGT-Edge-02...")
    tn = telnetlib.Telnet(HOST, 5008, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nadmin\r\nFortinet2025!\r\n")
    time.sleep(1)
    
    cmds = [
        "config vpn ipsec phase1-interface",
        "edit VPN-CiscoSite",
        "set proposal aes256-sha1",
        "set dhgrp 14",
        "set dpd-retrycount 3",
        "set dpd-retryinterval 5",
        "next",
        "end",
        "config vpn ipsec phase2-interface",
        "edit VPN-CiscoSite-p2",
        "set proposal aes256-sha1",
        "set dhgrp 14",
        "set auto-negotiate enable",
        "next",
        "end"
    ]
    for c in cmds:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.1)
    time.sleep(2)
    tn.write(b"diagnose vpn tunnel list\r\n")
    time.sleep(1)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("[+] FortiGate salida:\n", out[-500:])
    tn.close()

if __name__ == "__main__":
    align_cisco()
    align_fgt()
