import telnetlib
import time

HOST = "192.168.6.129"

def test_pings():
    # 1. From FortiGate: ping 200.25.7.5 (ISP) and 200.25.7.2 (Cisco Edge)
    tn = telnetlib.Telnet(HOST, 5008, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\nadmin\r\nFortinet2025!\r\nexecute ping 200.25.7.5\r\nexecute ping 200.25.7.2\r\n")
    time.sleep(5)
    out_fgt = tn.read_very_eager().decode('ascii', errors='ignore')
    print("--- FGT Ping Output ---")
    print(out_fgt[-600:])
    tn.close()

    # 2. From ISP-Router: ping both
    tn2 = telnetlib.Telnet(HOST, 5000, timeout=5)
    time.sleep(0.5)
    tn2.write(b"\r\nenable\r\nping 200.25.7.2\r\nping 200.25.7.6\r\n")
    time.sleep(3)
    out_isp = tn2.read_very_eager().decode('ascii', errors='ignore')
    print("--- ISP Ping Output ---")
    print(out_isp[-600:])
    tn2.close()

if __name__ == "__main__":
    test_pings()
