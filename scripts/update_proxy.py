import subprocess

proxy_code = """import socket
import select
import sys

LOCAL_PORT = 8080
TARGET_IP = '192.168.42.143'
TARGET_PORT = 80

def proxy_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', LOCAL_PORT))
    server.listen(10)
    print(f'Proxy running on 0.0.0.0:{LOCAL_PORT} -> {TARGET_IP}:{TARGET_PORT}')
    
    while True:
        client_sock, client_addr = server.accept()
        try:
            target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_sock.connect((TARGET_IP, TARGET_PORT))
        except Exception as e:
            client_sock.close()
            continue
            
        sockets = [client_sock, target_sock]
        while True:
            r, _, _ = select.select(sockets, [], [], 10)
            if not r:
                break
            for s in r:
                data = s.recv(4096)
                if not data:
                    break
                other = target_sock if s is client_sock else client_sock
                other.sendall(data)
            else:
                continue
            break
        client_sock.close()
        target_sock.close()

if __name__ == '__main__':
    proxy_loop()
"""

with open("Scripts/fgt_proxy_infra2.py", "w") as f:
    f.write(proxy_code)

# Copy to GNS3 VM
subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", "Scripts/fgt_proxy_infra2.py", "gns3@192.168.6.129:/home/gns3/fgt_gui_proxy.py"], check=True)
# Restart proxy on GNS3 VM
cmd = "pkill -f fgt_gui_proxy.py; nohup python3 /home/gns3/fgt_gui_proxy.py >/dev/null 2>&1 & sleep 1; ps aux | grep proxy"
res = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "gns3@192.168.6.129", cmd], capture_output=True, text=True)
print("Proxy status:\n", res.stdout)
