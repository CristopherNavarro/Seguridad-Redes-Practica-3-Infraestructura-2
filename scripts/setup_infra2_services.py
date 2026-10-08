import telnetlib
import time

HOST = "192.168.6.129"

HTML_JUMP = """<!DOCTYPE html>
<html>
<head><meta charset='utf-8'><title>ITLA RemoteApp Web Client</title></head>
<body style='font-family:sans-serif;background:#0f172a;color:#f8fafc;padding:30px;'>
  <h1 style='color:#38bdf8;'>RemoteApp and Desktop Connections - Web Client</h1>
  <p>Jump Server Gateway (10.25.30.2) | ITLA Seguridad de Redes (2025-0720)</p>
  <div style='background:#1e293b;padding:20px;border-radius:8px;margin-top:20px;'>
    <h3>Aplicaciones Publicadas:</h3>
    <ul>
      <li><b>Web ERP / Sistema de Caja</b>: [Publicado] - HTTP / HTTPS</li>
      <li><b>PuTTY SSH Client</b>: [Privilegiado] - Puerto 22</li>
      <li><b>Remote Desktop (RDP)</b>: [Privilegiado] - Puerto 3389</li>
    </ul>
  </div>
</body>
</html>
"""

def setup_jump_server():
    print("[*] Configurando Srv-JumpServer (puerto 5010)...")
    tn = telnetlib.Telnet(HOST, 5010, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    
    length = len(HTML_JUMP.encode('utf-8'))
    http_resp = f"HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nContent-Length: {length}\\r\\nConnection: close\\r\\n\\r\\n{HTML_JUMP}"
    
    script = f"""cat << 'EOF' > /root/start_jump_services.sh
#!/bin/sh
killall nc 2>/dev/null
pkill -f start_jump_services.sh 2>/dev/null
while true; do
    echo -e "{http_resp}" | nc -l -p 80
    sleep 0.1
done &
while true; do
    echo "SSH-2.0-OpenSSH_8.9_JumpServer" | nc -l -p 22
    sleep 0.1
done &
while true; do
    echo "RDP-RemoteApp-Server-Ready" | nc -l -p 3389
    sleep 0.1
done &
EOF
chmod +x /root/start_jump_services.sh
/root/start_jump_services.sh >/dev/null 2>&1 &
sleep 1
"""
    for l in script.strip().splitlines():
        tn.write(l.encode('ascii') + b"\r\n")
        time.sleep(0.15)
        
    time.sleep(2)
    tn.write(b"netstat -tuln; wget -q -O - http://127.0.0.1 | head -n 5\r\n")
    time.sleep(1)
    print("Jump Status:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    tn.close()

def setup_web_caja():
    print("[*] Configurando Srv-Web-Caja (puerto 5012)...")
    tn = telnetlib.Telnet(HOST, 5012, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    
    html_caja = "<html><body><h1>SISTEMA DE FACTURACION Y CAJA</h1><p>Conexion Segura TLS/HTTPS.</p></body></html>"
    len_caja = len(html_caja.encode('utf-8'))
    https_resp = f"HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nContent-Length: {len_caja}\\r\\nConnection: close\\r\\n\\r\\n{html_caja}"
    http_resp = f"HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\nContent-Length: 30\\r\\nConnection: close\\r\\n\\r\\n<h1>HTTP Desprotegido</h1>"

    script = f"""cat << 'EOF' > /root/start_caja_services.sh
#!/bin/sh
killall nc 2>/dev/null
pkill -f start_caja_services.sh 2>/dev/null
while true; do
    echo -e "{https_resp}" | nc -l -p 443
    sleep 0.1
done &
while true; do
    echo -e "{http_resp}" | nc -l -p 80
    sleep 0.1
done &
while true; do
    echo "SSH-2.0-OpenSSH_8.9_WebCaja" | nc -l -p 22
    sleep 0.1
done &
while true; do
    echo "RDP-WebCaja-Ready" | nc -l -p 3389
    sleep 0.1
done &
EOF
chmod +x /root/start_caja_services.sh
/root/start_caja_services.sh >/dev/null 2>&1 &
sleep 1
"""
    for l in script.strip().splitlines():
        tn.write(l.encode('ascii') + b"\r\n")
        time.sleep(0.15)
        
    time.sleep(2)
    tn.write(b"netstat -tuln\r\n")
    time.sleep(1)
    print("Caja Status:\n", tn.read_very_eager().decode('ascii', errors='ignore'))
    tn.close()

if __name__ == "__main__":
    setup_jump_server()
    setup_web_caja()
