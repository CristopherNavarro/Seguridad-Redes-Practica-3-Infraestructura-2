import telnetlib
import time

HOST = "192.168.6.129"

HTML_JUMP_PORTAL = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ITLA - RDP RemoteApp Web Client Portal</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
.header { background: #1e293b; padding: 20px 30px; border-radius: 12px; margin-bottom: 25px; border-left: 6px solid #3b82f6; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
h1 { margin: 0 0 8px 0; font-size: 24px; color: #38bdf8; }
p { margin: 0; color: #94a3b8; font-size: 14px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; transition: transform 0.2s; }
.card:hover { transform: translateY(-3px); border-color: #38bdf8; }
.badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 12px; }
.badge-pub { background: #065f46; color: #34d399; }
.badge-priv { background: #831843; color: #f472b6; }
.app-title { font-size: 18px; font-weight: bold; color: #f1f5f9; margin-bottom: 8px; }
.app-desc { font-size: 13px; color: #94a3b8; margin-bottom: 15px; }
.status { font-size: 12px; font-weight: 600; color: #22c55e; }
.footer { margin-top: 30px; padding: 15px; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid #1e293b; }
</style>
</head>
<body>
<div class="header">
  <h1>RemoteApp and Desktop Connections - Web Client</h1>
  <p>Jump Server Gateway (10.25.30.2) | ITLA Seguridad de Redes - Pr&aacute;ctica 3</p>
</div>
<div class="grid">
  <div class="card">
    <span class="badge badge-pub">Acceso P&uacute;blico / No Privilegiado</span>
    <div class="app-title">Web ERP / Sistema de Caja</div>
    <div class="app-desc">Portal web financiero y de facturaci&oacute;n corporativo publicado en l&iacute;nea.</div>
    <div class="status">&bull; Publicado y Activo (HTTP / HTTPS)</div>
  </div>
  <div class="card">
    <span class="badge badge-priv">Acceso Restringido / Privilegiado</span>
    <div class="app-title">PuTTY SSH Client</div>
    <div class="app-desc">Cliente de terminal SSH seguro para administraci&oacute;n de infraestructura.</div>
    <div class="status">&bull; Solo Rol Privilegiado (Puerto 22)</div>
  </div>
  <div class="card">
    <span class="badge badge-priv">Acceso Restringido / Privilegiado</span>
    <div class="app-title">Remote Desktop Connection (RDP)</div>
    <div class="app-desc">Sesi&oacute;n de escritorio remoto completo hacia servidores internos autorizados.</div>
    <div class="status">&bull; Solo Rol Privilegiado (Puerto 3389)</div>
  </div>
</div>
<div class="footer">
  Jump Server de Producci&oacute;n | Autenticaci&oacute;n Centralizada FortiGate VPN &bull; Estudiante: Cristopher Navarro (2025-0720)
</div>
</body>
</html>
"""

def send_docker_cmds(name, port, cmds):
    print(f"[*] Configurando {name} (puerto {port})...", flush=True)
    try:
        tn = telnetlib.Telnet(HOST, port, timeout=10)
        time.sleep(0.5)
        tn.write(b"\r\n")
        time.sleep(0.5)
        for c in cmds:
            tn.write(c.encode('ascii') + b"\n")
            time.sleep(0.2)
        time.sleep(1)
        out = tn.read_very_eager().decode('ascii', errors='ignore')
        tn.close()
        print(f"[+] {name} configurado exitosamente.", flush=True)
        return True, out
    except Exception as e:
        print(f"[-] Error en {name}: {e}", flush=True)
        return False, str(e)

def main():
    # 1. PC-User-NoPriv (10.25.10.10/25, gw 10.25.10.1)
    nopriv_cmds = [
        "ip addr flush dev eth0",
        "ip addr add 10.25.10.10/25 dev eth0",
        "ip link set eth0 up",
        "ip route add default via 10.25.10.1",
        "hostname PC-User-NoPriv"
    ]
    send_docker_cmds("PC-User-NoPriv", 5004, nopriv_cmds)

    # 2. PC-User-Priv (10.25.10.20/25, gw 10.25.10.1)
    priv_cmds = [
        "ip addr flush dev eth0",
        "ip addr add 10.25.10.20/25 dev eth0",
        "ip link set eth0 up",
        "ip route add default via 10.25.10.1",
        "hostname PC-User-Priv"
    ]
    send_docker_cmds("PC-User-Priv", 5006, priv_cmds)

    # 3. Srv-JumpServer (10.25.30.2/29, gw 10.25.30.1)
    # Start web portal on port 80, mock RDP on 3389, mock SSH on 22
    jump_cmds = [
        "ip addr flush dev eth0",
        "ip addr add 10.25.30.2/29 dev eth0",
        "ip link set eth0 up",
        "ip route add default via 10.25.30.1",
        "hostname Srv-JumpServer",
        "mkdir -p /var/www/html",
        "cat << 'EOF' > /var/www/html/index.html\n" + HTML_JUMP_PORTAL + "\nEOF",
        "pkill -f http.server; pkill -f nc",
        "nohup python3 -m http.server 80 -d /var/www/html >/dev/null 2>&1 &",
        "nohup nc -lk -p 3389 -e echo 'RDP-RemoteApp-Server-Ready' >/dev/null 2>&1 &",
        "nohup nc -lk -p 22 -e echo 'SSH-2.0-OpenSSH_JumpServer_8.8' >/dev/null 2>&1 &"
    ]
    send_docker_cmds("Srv-JumpServer", 5010, jump_cmds)

    # 4. Srv-Web-Caja (10.25.20.2/29, gw 10.25.20.1)
    web_cmds = [
        "ip addr flush dev eth0",
        "ip addr add 10.25.20.2/29 dev eth0",
        "ip link set eth0 up",
        "ip route add default via 10.25.20.1",
        "hostname Srv-Web-Caja",
        "mkdir -p /var/www/caja",
        "echo '<h1>ITLA - Sistema Web Caja (HTTPS 443)</h1><p>Conexion segura establecida.</p>' > /var/www/caja/index.html",
        "pkill -f http.server; pkill -f nc",
        # Listen on 443 (mock HTTPS / web caja)
        "nohup nc -lk -p 443 -e echo -e 'HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\n\\r\\n<h1>Sistema Web Caja</h1>' >/dev/null 2>&1 &",
        # Listen on 80 (HTTP) to test deny policy!
        "nohup nc -lk -p 80 -e echo -e 'HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\n\\r\\n<h1>HTTP Desprotegido</h1>' >/dev/null 2>&1 &",
        # Listen on 22 (SSH)
        "nohup nc -lk -p 22 -e echo 'SSH-2.0-OpenSSH_WebCaja_8.8' >/dev/null 2>&1 &",
        # Listen on 3389 (RDP)
        "nohup nc -lk -p 3389 -e echo 'RDP-WebCaja-Service-Ready' >/dev/null 2>&1 &"
    ]
    send_docker_cmds("Srv-Web-Caja", 5012, web_cmds)

if __name__ == "__main__":
    main()
