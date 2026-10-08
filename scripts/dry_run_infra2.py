import telnetlib
import time
import os

HOST = "192.168.6.129"
OUTPUT_FILE = r"c:\Users\crist\Downloads\Tareas Seguridad de Redes (GNS3)\Archivos para mi\bitacora_ensayo_infraestructura_2.txt"

def run_command(tn, cmd, sleep_time=2):
    tn.write(cmd.encode('ascii') + b"\r\n")
    time.sleep(sleep_time)
    out = tn.read_very_eager().decode('ascii', errors='ignore')
    return out.strip()

def main():
    log_data = []
    log_data.append("================================================================================")
    log_data.append("BITÁCORA OFICIAL DEL SIMULACRO Y ENSAYO GENERAL (DRY RUN) - INFRAESTRUCTURA 2")
    log_data.append("Estudiante: Cristopher Navarro (Matrícula: 2025-0720)")
    log_data.append("Docente: Jonathan Esteban Rondón Corniel | Asignatura: Seguridad de Redes")
    log_data.append("Fecha de Certificación: Octubre 2026")
    log_data.append("================================================================================\n")

    # 1. Cisco Edge
    print("[*] Ensayando comandos en Cisco-Edge-01...", flush=True)
    log_data.append("### 1. ESTADO DE INTERFACES Y TÚNEL IPSEC EN CISCO-EDGE-01 (Router Perimetral Cliente)")
    try:
        tn = telnetlib.Telnet(HOST, 5001, timeout=5)
        time.sleep(0.5)
        tn.write(b"\r\nenable\r\nterminal length 0\r\n")
        time.sleep(0.5)
        
        cmds = ["show ip interface brief", "show crypto isakmp sa", "show crypto ipsec sa"]
        for c in cmds:
            out = run_command(tn, c, sleep_time=1.5)
            log_data.append(f">>> {c}\n{out}\n")
        tn.close()
    except Exception as e:
        log_data.append(f"[-] Error en Cisco: {e}\n")

    # 2. FortiGate
    print("[*] Ensayando comandos en FGT-Edge-02...", flush=True)
    log_data.append("### 2. ESTADO DEL TÚNEL IPSEC Y POLÍTICAS EN FGT-EDGE-02 (Firewall Central)")
    try:
        tn = telnetlib.Telnet(HOST, 5008, timeout=5)
        time.sleep(0.5)
        tn.write(b"\r\nadmin\r\nFortinet2025!\r\nconfig system console\r\nset output standard\r\nend\r\n")
        time.sleep(1)
        
        cmds = ["diagnose vpn tunnel list", "show firewall policy"]
        for c in cmds:
            out = run_command(tn, c, sleep_time=1.5)
            log_data.append(f">>> {c}\n{out}\n")
        tn.close()
    except Exception as e:
        log_data.append(f"[-] Error en FortiGate: {e}\n")

    # 3. PC-User-NoPriv
    print("[*] Ensayando comandos en PC-User-NoPriv...", flush=True)
    log_data.append("### 3. DEMOSTRACIÓN DESDE ESTACIÓN NO PRIVILEGIADA (PC-User-NoPriv: 10.25.10.10)")
    try:
        tn = telnetlib.Telnet(HOST, 5004, timeout=5)
        time.sleep(0.5)
        tn.write(b"\r\n\r\n")
        time.sleep(0.5)
        
        cmds = [
            ("ip addr show dev eth0", 1),
            ("wget -q -O - -T 3 http://10.25.30.2", 2),
            ("nc -zv -w 3 10.25.30.2 22", 3),
            ("nc -zv -w 3 10.25.20.2 443", 3)
        ]
        for c, t in cmds:
            out = run_command(tn, c, sleep_time=t)
            log_data.append(f">>> {c}\n{out}\n")
        tn.close()
    except Exception as e:
        log_data.append(f"[-] Error en PC-User-NoPriv: {e}\n")

    # 4. PC-User-Priv
    print("[*] Ensayando comandos en PC-User-Priv...", flush=True)
    log_data.append("### 4. DEMOSTRACIÓN DESDE ESTACIÓN PRIVILEGIADA (PC-User-Priv: 10.25.10.20)")
    try:
        tn = telnetlib.Telnet(HOST, 5006, timeout=5)
        time.sleep(0.5)
        tn.write(b"\r\n\r\n")
        time.sleep(0.5)
        
        cmds = [
            ("ip addr show dev eth0", 1),
            ("wget -q -O - -T 3 http://10.25.30.2", 2),
            ("nc -zv -w 3 10.25.30.2 22", 2),
            ("nc -zv -w 3 10.25.30.2 3389", 2),
            ("nc -zv -w 3 10.25.20.2 443", 3)
        ]
        for c, t in cmds:
            out = run_command(tn, c, sleep_time=t)
            log_data.append(f">>> {c}\n{out}\n")
        tn.close()
    except Exception as e:
        log_data.append(f"[-] Error en PC-User-Priv: {e}\n")

    # 5. Srv-JumpServer
    print("[*] Ensayando comandos en Srv-JumpServer...", flush=True)
    log_data.append("### 5. DEMOSTRACIÓN DE ACCESO RESTRINGIDO DESDE JUMP SERVER (10.25.30.2) A WEB SERVER (10.25.20.2)")
    try:
        tn = telnetlib.Telnet(HOST, 5010, timeout=5)
        time.sleep(0.5)
        tn.write(b"\r\n\r\n")
        time.sleep(0.5)
        
        cmds = [
            ("nc -zv -w 3 10.25.20.2 443", 2),
            ("nc -zv -w 3 10.25.20.2 22", 2),
            ("nc -zv -w 3 10.25.20.2 3389", 2),
            ("nc -zv -w 3 10.25.20.2 80", 3)
        ]
        for c, t in cmds:
            out = run_command(tn, c, sleep_time=t)
            log_data.append(f">>> {c}\n{out}\n")
        tn.close()
    except Exception as e:
        log_data.append(f"[-] Error en Srv-JumpServer: {e}\n")

    final_content = "\n".join(log_data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(final_content)
    print(f"\n[+] ¡Ensayo general completado exitosamente! Bitácora guardada en:\n{OUTPUT_FILE}")

if __name__ == "__main__":
    main()
