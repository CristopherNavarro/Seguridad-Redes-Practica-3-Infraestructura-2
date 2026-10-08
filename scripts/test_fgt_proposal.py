import telnetlib
import time

HOST = "192.168.6.129"
tn = telnetlib.Telnet(HOST, 5008, timeout=5)
time.sleep(0.5)
tn.write(b"\r\nconfig vpn ipsec phase1-interface\r\nedit VPN-CiscoSite\r\nset proposal aes256-sha1\r\nnext\r\nend\r\nshow vpn ipsec phase1-interface VPN-CiscoSite\r\n")
time.sleep(2)
out = tn.read_very_eager().decode('ascii', errors='ignore')
print(out)
tn.close()
