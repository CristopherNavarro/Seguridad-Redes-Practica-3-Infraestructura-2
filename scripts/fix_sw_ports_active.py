import telnetlib
import time

HOST = "192.168.6.129"
PORT = 5002

tn = telnetlib.Telnet(HOST, PORT, timeout=5)
time.sleep(0.5)
tn.write(b"\r\nterminal length 0\r\nconfigure terminal\r\n")
time.sleep(0.5)

cmds = [
    "interface Gi1/1",
    " description ACCESS_PC_USER_NOPRIV",
    " switchport mode access",
    " switchport access vlan 10",
    " switchport nonegotiate",
    " spanning-tree portfast",
    " spanning-tree bpduguard enable",
    " no shutdown",
    "interface Gi2/1",
    " description ACCESS_PC_USER_PRIV",
    " switchport mode access",
    " switchport access vlan 10",
    " switchport nonegotiate",
    " spanning-tree portfast",
    " spanning-tree bpduguard enable",
    " no shutdown",
    "end",
    "write memory"
]

for c in cmds:
    tn.write(c.encode('ascii') + b"\r\n")
    time.sleep(0.1)

time.sleep(2)
tn.write(b"show interfaces status\r\n")
time.sleep(1.5)
out = tn.read_very_eager().decode('ascii', errors='ignore')
print(out)
tn.close()
