import telnetlib
import time

HOST = "192.168.6.129"

print("--- CISCO IPSEC STATUS ---")
tn = telnetlib.Telnet(HOST, 5001, timeout=5)
time.sleep(0.5)
tn.write(b"\r\nenable\r\nterminal length 0\r\nshow crypto isakmp sa\r\nshow crypto ipsec sa\r\n")
time.sleep(1.5)
print(tn.read_very_eager().decode('ascii', errors='ignore'))
tn.close()

print("--- FORTIGATE IPSEC STATUS ---")
tn2 = telnetlib.Telnet(HOST, 5008, timeout=5)
time.sleep(0.5)
tn2.write(b"\r\nadmin\r\nFortinet2025!\r\ndiagnose vpn ike gateway list\r\ndiagnose vpn tunnel list\r\n")
time.sleep(1.5)
print(tn2.read_very_eager().decode('ascii', errors='ignore'))
tn2.close()
