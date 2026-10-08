import telnetlib
import time

HOST = "192.168.6.129"
PORT = 5002

tn = telnetlib.Telnet(HOST, PORT, timeout=5)
time.sleep(0.5)
tn.write(b"\r\n\r\nterminal length 0\r\nshow interfaces status\r\nshow cdp neighbors\r\n")
time.sleep(2)
out = tn.read_very_eager().decode('ascii', errors='ignore')
print(out)
tn.close()
