import subprocess

ssh_cmds = [
    "pkill -f fgt_gui_proxy.py || true",
    "sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.42.143:80",
    "sudo iptables -t nat -A PREROUTING -p tcp --dport 8443 -j DNAT --to-destination 192.168.42.143:443",
    "sudo iptables -t nat -A POSTROUTING -p tcp -d 192.168.42.143 --dport 80 -j MASQUERADE",
    "sudo iptables -t nat -A POSTROUTING -p tcp -d 192.168.42.143 --dport 443 -j MASQUERADE"
]

remote_script = "; ".join(ssh_cmds)
print("Ejecutando en GNS3 VM:", remote_script)
res = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "gns3@192.168.6.129", remote_script], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
