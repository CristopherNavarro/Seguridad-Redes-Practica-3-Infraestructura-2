import telnetlib
import time

HOST = "192.168.6.129"

def run_pc_tests(name, port, tests):
    print(f"\n==================================================")
    print(f"PRUEBAS EN CLIENTE: {name} (Puerto {port})")
    print(f"==================================================")
    tn = telnetlib.Telnet(HOST, port, timeout=5)
    time.sleep(0.5)
    tn.write(b"\r\n\r\n")
    time.sleep(0.5)
    for desc, cmd in tests:
        print(f"[*] {desc}")
        tn.write(cmd.encode('ascii') + b"\r\n")
        time.sleep(2)
        out = tn.read_very_eager().decode('ascii', errors='ignore')
        lines = [l.strip() for l in out.strip().splitlines() if l.strip()]
        for l in lines[-4:]:
            print(f"    {l}")
    tn.close()

def main():
    nopriv_tests = [
        ("Ping al Gateway local (10.25.10.1)", "ping -c 2 10.25.10.1"),
        ("Acceso Web al Jump Server (HTTP 80) -> DEBE PERMITIR", "wget -q -O - -T 3 http://10.25.30.2"),
        ("Acceso SSH al Jump Server (Puerto 22) -> POLITICA DENY EXPLICITA", "nc -zv -w 2 10.25.30.2 22"),
        ("Acceso Directo al Web Server Caja (Puerto 443) -> DEBE DENEGAR (Sin salto)", "nc -zv -w 2 10.25.20.2 443")
    ]
    run_pc_tests("PC-User-NoPriv", 5004, nopriv_tests)

    priv_tests = [
        ("Ping al Gateway local (10.25.10.1)", "ping -c 2 10.25.10.1"),
        ("Acceso Web al Jump Server (HTTP 80) -> DEBE PERMITIR", "wget -q -O - -T 3 http://10.25.30.2"),
        ("Acceso SSH (PuTTY) al Jump Server (Puerto 22) -> DEBE PERMITIR", "nc -zv -w 2 10.25.30.2 22"),
        ("Acceso RDP al Jump Server (Puerto 3389) -> DEBE PERMITIR", "nc -zv -w 2 10.25.30.2 3389"),
        ("Acceso Directo al Web Server Caja (Puerto 443) -> DEBE DENEGAR (Sin salto)", "nc -zv -w 2 10.25.20.2 443")
    ]
    run_pc_tests("PC-User-Priv", 5006, priv_tests)

    jump_tests = [
        ("Acceso desde Jump Server a Web Server Caja (HTTPS 443) -> DEBE PERMITIR", "nc -zv -w 2 10.25.20.2 443"),
        ("Acceso desde Jump Server a Web Server Caja (SSH 22) -> DEBE PERMITIR", "nc -zv -w 2 10.25.20.2 22"),
        ("Acceso desde Jump Server a Web Server Caja (RDP 3389) -> DEBE PERMITIR", "nc -zv -w 2 10.25.20.2 3389"),
        ("Acceso desde Jump Server a Web Server Caja (HTTP 80) -> RESTRINGIDO / BLOQUEADO", "nc -zv -w 2 10.25.20.2 80")
    ]
    run_pc_tests("Srv-JumpServer", 5010, jump_tests)

if __name__ == "__main__":
    main()
