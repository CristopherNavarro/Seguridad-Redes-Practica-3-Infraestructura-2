import telnetlib
import time

HOST = "192.168.6.129"

def check_sw():
    print("--- SW-Client Status ---")
    tn = telnetlib.Telnet(HOST, 5002, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nenable\r\nterminal length 0\r\n")
    time.sleep(0.5)
    tn.write(b"show ip interface brief\r\nshow interfaces status\r\nshow interfaces trunk\r\n")
    time.sleep(1.5)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print(out)
    tn.close()

def check_cisco_edge():
    print("--- Cisco-Edge-01 Status ---")
    tn = telnetlib.Telnet(HOST, 5001, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nenable\r\nterminal length 0\r\n")
    time.sleep(0.5)
    tn.write(b"show ip interface brief\r\n")
    time.sleep(1)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print(out)
    tn.close()

def fix_fgt():
    print("--- Fixing FGT-Edge-02 Default Route ---")
    tn = telnetlib.Telnet(HOST, 5008, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nadmin\r\nFortinet2025!\r\n")
    time.sleep(1)
    tn.write(b"config system console\r\nset output standard\r\nend\r\n")
    time.sleep(0.5)
    cmds = [
        "config system interface",
        "edit port4",
        "set defaultgw disable",
        "next",
        "end",
        "config router static",
        "edit 1",
        "set dst 0.0.0.0 0.0.0.0",
        "set gateway 200.25.7.5",
        "set device port1",
        "next",
        "end",
        "get router info routing-table all"
    ]
    for c in cmds:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.1)
    time.sleep(1)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print(out[-400:])
    tn.close()

if __name__ == "__main__":
    check_cisco_edge()
    check_sw()
    fix_fgt()
