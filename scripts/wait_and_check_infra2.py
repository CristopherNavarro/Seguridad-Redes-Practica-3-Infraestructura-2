import telnetlib
import time

HOST = "192.168.6.129"
CONSOLES = {
    "ISP-Router": 5000,
    "Cisco-Edge-01": 5001,
    "SW-Client": 5002,
    "PC-User-NoPriv": 5004,
    "PC-User-Priv": 5006,
    "FGT-Edge-02": 5008,
    "Srv-JumpServer": 5010,
    "Srv-Web-Caja": 5012
}

def check_console(name, port):
    try:
        tn = telnetlib.Telnet(HOST, port, timeout=3)
        time.sleep(0.5)
        tn.write(b"\r\n")
        time.sleep(0.5)
        out = tn.read_very_eager().decode('ascii', errors='ignore')
        tn.close()
        last_line = out.strip().split('\n')[-1] if out.strip() else "(sin salida)"
        print(f"[{name}:{port}] RESPUESTA: {last_line}")
        return True, out
    except Exception as e:
        print(f"[{name}:{port}] ERROR: {e}")
        return False, str(e)

def main():
    print("Verificando estado de consolas en Infraestructura 2...")
    for name, port in CONSOLES.items():
        check_console(name, port)

if __name__ == "__main__":
    main()
