import telnetlib
import time

HOST = "192.168.6.129"

def set_cisco():
    print("[*] Configurando Cisco con DES-SHA1...")
    tn = telnetlib.Telnet(HOST, 5001, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nenable\r\nterminal length 0\r\nconfigure terminal\r\n")
    time.sleep(0.5)
    cmds = [
        "no crypto isakmp policy 10",
        "crypto isakmp policy 10",
        " encr des",
        " hash sha",
        " authentication pre-share",
        " group 14",
        " lifetime 86400",
        "exit",
        "no crypto ipsec transform-set TSET",
        "crypto ipsec transform-set TSET esp-des esp-sha-hmac",
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
    time.sleep(1)
    tn.close()
    print("[+] Cisco listo.")

def set_fgt():
    print("[*] Configurando FortiGate con DES-SHA1...")
    tn = telnetlib.Telnet(HOST, 5008, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nadmin\r\nFortinet2025!\r\n")
    time.sleep(1)
    cmds = [
        "config vpn ipsec phase1-interface",
        "edit VPN-CiscoSite",
        "set proposal des-sha1",
        "set dhgrp 14",
        "next",
        "end",
        "config vpn ipsec phase2-interface",
        "edit VPN-CiscoSite-p2",
        "set proposal des-sha1",
        "set dhgrp 14",
        "set auto-negotiate enable",
        "next",
        "end"
    ]
    for c in cmds:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.1)
    time.sleep(1)
    tn.close()
    print("[+] FortiGate listo.")

if __name__ == "__main__":
    set_cisco()
    set_fgt()
