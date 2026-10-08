import telnetlib
import time
import sys

HOST = "192.168.6.129"
PORT = 5008

def login_and_configure():
    print("[*] Conectando a FGT-Edge-02 (puerto 5008)...", flush=True)
    tn = telnetlib.Telnet(HOST, PORT, timeout=10)
    time.sleep(1)
    tn.write(b"\x03\r\n")
    time.sleep(1)
    buf = tn.read_very_eager().decode('ascii', errors='ignore')
    
    # Si está esperando login o password
    if "login:" not in buf and "Password:" not in buf and "#" not in buf:
        tn.write(b"\r\n")
        time.sleep(1)
        buf = tn.read_very_eager().decode('ascii', errors='ignore')

    print(f"[*] Buffer inicial: {repr(buf)}", flush=True)

    if "#" in buf:
        print("[+] Ya estamos en el prompt # de FortiGate!", flush=True)
    else:
        # Intentar login con Fortinet2025! primero en caso de que ya se haya cambiado
        if "login:" in buf:
            tn.write(b"admin\r")
            time.sleep(1)
            buf = tn.read_very_eager().decode('ascii', errors='ignore')
            
        if "Password:" in buf:
            tn.write(b"Fortinet2025!\r")
            time.sleep(2)
            buf = tn.read_very_eager().decode('ascii', errors='ignore')
            
        if "#" not in buf:
            # Si falló, intentar reseteo de password desde cero
            print("[*] Reintentando secuencia inicial de cambio de clave...", flush=True)
            tn.write(b"\x03\r\n")
            time.sleep(1)
            tn.read_until(b"login: ", timeout=5)
            tn.write(b"admin\r")
            tn.read_until(b"Password: ", timeout=5)
            tn.write(b"\r")
            tn.read_until(b"New Password: ", timeout=5)
            tn.write(b"Fortinet2025!\r")
            tn.read_until(b"Confirm Password: ", timeout=5)
            tn.write(b"Fortinet2025!\r")
            time.sleep(2)
            buf = tn.read_very_eager().decode('ascii', errors='ignore')

    print(f"[*] Estado tras autenticación: {repr(buf)}", flush=True)
    tn.write(b"\r\n")
    time.sleep(1)
    buf_prompt = tn.read_very_eager().decode('ascii', errors='ignore')
    print(f"[*] Prompt confirmado: {repr(buf_prompt)}", flush=True)

    # Regla 7: Desactivar paginación inmediatamente
    tn.write(b"config system console\r\nset output standard\r\nend\r\n")
    time.sleep(1)
    print("[+] Paginación desactivada.", flush=True)

    # Configuración completa
    commands = [
        "config system global",
        "set hostname FGT-Edge-02",
        "set timezone 04",
        "set admintimeout 480",
        "end",
        
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
        
        "config router static",
        "edit 1",
        "set dst 0.0.0.0 0.0.0.0",
        "set gateway 200.25.7.5",
        "set device port1",
        "next",
        "end",
        
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
        
        "config vpn ipsec phase2-interface",
        "edit VPN-CiscoSite-p2",
        "set phase1name VPN-CiscoSite",
        "set proposal aes256-sha256",
        "set dhgrp 14",
        "set src-subnet 10.25.30.0 255.255.255.248",
        "set dst-subnet 10.25.10.0 255.255.255.128",
        "next",
        "end",
        
        "config router static",
        "edit 2",
        "set dst 10.25.10.0 255.255.255.128",
        "set device VPN-CiscoSite",
        "next",
        "end",
        
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
        
        "config firewall policy",
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

    print(f"[*] Aplicando {len(commands)} comandos a FGT-Edge-02...", flush=True)
    for c in commands:
        tn.write(c.encode('ascii') + b"\r\n")
        time.sleep(0.04)

    time.sleep(2)
    tn.write(b"get system status\r\n")
    time.sleep(1)
    status_out = tn.read_very_eager().decode('ascii', errors='ignore')
    print("[+] Resumen de Estado del Sistema:\n", status_out[:400], flush=True)
    tn.close()
    return True

if __name__ == "__main__":
    login_and_configure()
