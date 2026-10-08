import telnetlib
import time

HOST = "192.168.6.129"

def fix_server(name, port, commands):
    print(f"[*] Configurando listeners en {name} (puerto {port})...")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    tn.write(b"killall nc 2>/dev/null\r\n")
    time.sleep(0.5)
    for c in commands:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.3)
    time.sleep(1)
    tn.write(b"netstat -tuln; ps aux | grep nc\r\n")
    time.sleep(1)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    print(out)
    tn.close()

def main():
    # 1. Srv-JumpServer (10.25.30.2)
    jump_cmds = [
        "nohup nc -lk -p 80 -e echo -e 'HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nConnection: close\\r\\n\\r\\n<h1>ITLA RemoteApp Web Client Portal</h1><p>Jump Server 10.25.30.2</p>' >/dev/null 2>&1 &",
        "nohup nc -lk -p 22 -e echo 'SSH-2.0-OpenSSH_JumpServer_8.8' >/dev/null 2>&1 &",
        "nohup nc -lk -p 3389 -e echo 'RDP-RemoteApp-Server-Ready' >/dev/null 2>&1 &"
    ]
    fix_server("Srv-JumpServer", 5010, jump_cmds)

    # 2. Srv-Web-Caja (10.25.20.2)
    caja_cmds = [
        "nohup nc -lk -p 443 -e echo -e 'HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nConnection: close\\r\\n\\r\\n<h1>Sistema Web Caja HTTPS</h1>' >/dev/null 2>&1 &",
        "nohup nc -lk -p 80 -e echo -e 'HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nConnection: close\\r\\n\\r\\n<h1>HTTP Desprotegido</h1>' >/dev/null 2>&1 &",
        "nohup nc -lk -p 22 -e echo 'SSH-2.0-OpenSSH_WebCaja_8.8' >/dev/null 2>&1 &",
        "nohup nc -lk -p 3389 -e echo 'RDP-WebCaja-Service-Ready' >/dev/null 2>&1 &"
    ]
    fix_server("Srv-Web-Caja", 5012, caja_cmds)

if __name__ == "__main__":
    main()
