import telnetlib
import time
import sys

HOST = "192.168.6.129"
PORT = 5008

def log(msg):
    print(f"[*] {msg}", flush=True)

def login_and_configure():
    log("Conectando a FGT-Edge-02 (FortiGate 7.0.9 en puerto 5008)...")
    tn = telnetlib.Telnet(HOST, PORT, timeout=15)
    time.sleep(1)
    tn.write(b"\r\n")
    time.sleep(1)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    
    # 1. Login sequence
    if "login:" in buf:
        log("Enviando usuario 'admin'...")
        tn.write(b"admin\r\n")
        time.sleep(1)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        
    if "Password:" in buf:
        log("Enviando password en blanco...")
        tn.write(b"\r\n")
        time.sleep(1)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        
    if "New password:" in buf or "new password" in buf.lower():
        log("Estableciendo nueva contrasena 'Fortinet2025!'...")
        tn.write(b"Fortinet2025!\r\n")
        time.sleep(1)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        
    if "Confirm password:" in buf or "confirm" in buf.lower():
        log("Confirmando contrasena 'Fortinet2025!'...")
        tn.write(b"Fortinet2025!\r\n")
        time.sleep(2)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')
        
    # Check if already logged in or requires password
    if "Password:" in buf:
        tn.write(b"Fortinet2025!\r\n")
        time.sleep(1)
        
    # Send Enter to verify prompt
    tn.write(b"\r\n")
    time.sleep(1)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    log(f"Estado tras login: {buf[-150:]}")
    
    # Desactivar paginación (Regla 7)
    log("Desactivando paginacion en consola...")
    tn.write(b"config system console\r\nset output standard\r\nend\r\n")
    time.sleep(1)
    
    # Configuración de FortiGate
    config_commands = [
        # Hostname & global
        "config system global",
        "set hostname FGT-Edge-02",
        "set timezone 04",
        "set admintimeout 480",
        "end",
        
        # Interfaces
        "config system interface",
        "edit port1",
        "set mode static",
        "set ip 200.25.7.6 255.255.255.252",
        "set allowaccess ping https ssh http",
        "set description WAN_ISP",
        "next",
        "edit port2",
        "set mode static",
        "set ip 10.25.30.1 255.255.255.248",
        "set allowaccess ping https ssh http",
        "set description LAN_JUMP_SERVER",
        "next",
        "edit port3",
        "set mode static",
        "set ip 10.25.20.1 255.255.255.248",
        "set allowaccess ping https ssh http",
        "set description LAN_WEB_SERVER",
        "next",
        "edit port4",
        "set mode dhcp",
        "set allowaccess ping https ssh http",
        "set description MGMT_NAT",
        "next",
        "end",
        
        # Static routes
        "config router static",
        "edit 1",
        "set dst 0.0.0.0 0.0.0.0",
        "set gateway 200.25.7.5",
        "set device port1",
        "next",
        "end",
        
        # IPsec VPN Phase 1
        "config vpn ipsec phase1-interface",
        "edit VPN-CiscoSite",
        "set interface port1",
        "set peertype any",
        "set net-device disable",
        "set proposal aes256-sha256",
        "set dhgrp 14",
        "set remote-gw 200.25.7.2",
        "set psksecret ITLA2025!",
        "next",
        "end",
        
        # IPsec VPN Phase 2
        "config vpn ipsec phase2-interface",
        "edit VPN-CiscoSite-p2",
        "set phase1name VPN-CiscoSite",
        "set proposal aes256-sha256",
        "set dhgrp 14",
        "set src-subnet 10.25.30.0 255.255.255.248",
        "set dst-subnet 10.25.10.0 255.255.255.128",
        "next",
        "end",
        
        # Static route for Remote LAN via VPN
        "config router static",
        "edit 2",
        "set dst 10.25.10.0 255.255.255.128",
        "set device VPN-CiscoSite",
        "next",
        "end",
        
        # Firewall Objects
        "config firewall address",
        "edit User_NoPriv",
        "set subnet 10.25.10.10 255.255.255.255",
        "next",
        "edit User_Priv",
        "set subnet 10.25.10.20 255.255.255.255",
        "next",
        "edit Client_LAN_VLAN10",
        "set subnet 10.25.10.0 255.255.255.128",
        "next",
        "edit Jump_Server",
        "set subnet 10.25.30.2 255.255.255.255",
        "next",
        "edit Web_Server",
        "set subnet 10.25.20.2 255.255.255.255",
        "next",
        "edit LAN_Jump_Net",
        "set subnet 10.25.30.0 255.255.255.248",
        "next",
        "edit LAN_Web_Net",
        "set subnet 10.25.20.0 255.255.255.248",
        "next",
        "end",
        
        # Firewall Policies
        "config firewall policy",
        # 1. Deny SSH for NoPriv User
        "edit 1",
        "set name Deny_UserNoPriv_SSH",
        "set srcintf VPN-CiscoSite",
        "set dstintf port2 port3",
        "set srcaddr User_NoPriv",
        "set dstaddr all",
        "set action deny",
        "set schedule always",
        "set service SSH",
        "set logtraffic all",
        "next",
        # 2. Allow Web for NoPriv User to Jump Server
        "edit 2",
        "set name Allow_UserNoPriv_Web_Jump",
        "set srcintf VPN-CiscoSite",
        "set dstintf port2",
        "set srcaddr User_NoPriv",
        "set dstaddr Jump_Server",
        "set action accept",
        "set schedule always",
        "set service HTTP HTTPS",
        "set logtraffic all",
        "next",
        # 3. Allow Privileged User to Jump Server (Web, SSH/PuTTY, RDP)
        "edit 3",
        "set name Allow_UserPriv_Full_Jump",
        "set srcintf VPN-CiscoSite",
        "set dstintf port2",
        "set srcaddr User_Priv",
        "set dstaddr Jump_Server",
        "set action accept",
        "set schedule always",
        "set service HTTP HTTPS SSH RDP",
        "set logtraffic all",
        "next",
        # 4. Allow Jump Server to Web Server (ONLY HTTPS, RDP, SSH)
        "edit 4",
        "set name Allow_Jump_to_WebServer_Restricted",
        "set srcintf port2",
        "set dstintf port3",
        "set srcaddr Jump_Server",
        "set dstaddr Web_Server",
        "set action accept",
        "set schedule always",
        "set service HTTPS SSH RDP",
        "set logtraffic all",
        "next",
        # 5. Deny Direct VPN Access to Web Server
        "edit 5",
        "set name Deny_Direct_VPN_to_WebServer",
        "set srcintf VPN-CiscoSite",
        "set dstintf port3",
        "set srcaddr all",
        "set dstaddr all",
        "set action deny",
        "set schedule always",
        "set service ALL",
        "set logtraffic all",
        "next",
        "end"
    ]
    
    log(f"Aplicando {len(config_commands)} bloques de configuracion a FGT-Edge-02...")
    for cmd in config_commands:
        tn.write(cmd.encode('ascii') + b"\r\n")
        time.sleep(0.05)
        
    time.sleep(2)
    tn.write(b"\r\n")
    time.sleep(1)
    final_out = tn.read_very_eager().decode('ascii', errors='ignore')
    tn.close()
    log("[+] Configuracion enviada a FortiGate!")
    return True

if __name__ == "__main__":
    login_and_configure()
