#!/usr/bin/env python3
# language: Python 3.10+, file: lan_recon.py, target: Linux (Kali)
# Dépendances : nmap (apt install nmap), arp-scan (optionnel), python3
# Usage : sudo lan-recon

import subprocess
import re
import socket
import json
import sys
import os
from datetime import datetime
from pathlib import Path


# ============================================================
# 1. DÉTECTION AUTOMATIQUE DE LA PLAGE RÉSEAU
# ============================================================

def get_local_network() -> tuple[str, str]:
    """
    Lit `ip -o -4 addr show` pour trouver l'interface active et son IP/masque.
    Retourne (cidr, interface), ex: ("192.168.1.0/24", "wlan0").
    """
    result = subprocess.run(
        ["ip", "-o", "-4", "addr", "show"],
        capture_output=True, text=True, check=True
    )
    for line in result.stdout.splitlines():
        if " lo " in line:
            continue
        m = re.search(r"^\d+:\s+(\S+)\s+inet\s+(\d+\.\d+\.\d+\.\d+)/(\d+)", line)
        if m:
            iface, ip, prefix = m.group(1), m.group(2), int(m.group(3))
            octets = ip.split(".")
            if prefix == 24:
                network = f"{octets[0]}.{octets[1]}.{octets[2]}.0/24"
            elif prefix == 16:
                network = f"{octets[0]}.{octets[1]}.0.0/16"
            elif prefix == 8:
                network = f"{octets[0]}.0.0.0/8"
            else:
                network = f"{ip}/{prefix}"
            return network, iface
    raise RuntimeError("Aucune interface réseau active trouvée")


# ============================================================
# 2. SCAN NMAP POUR TROUVER LES MACHINES VIVANTES
# ============================================================

def nmap_discover(network: str) -> list[str]:
    """
    Lance `nmap -sn <network>` et extrait les IP des machines vivantes.
    Retourne une liste d'IP.
    """
    result = subprocess.run(
        ["nmap", "-sn", "-oG", "-", network],
        capture_output=True, text=True, check=True
    )
    alive = []
    for line in result.stdout.splitlines():
        m = re.search(r"^Host:\s+(\d+\.\d+\.\d+\.\d+)\s+.*Status:\s+Up", line)
        if m:
            alive.append(m.group(1))
    return alive


# ============================================================
# 3. RÉCUPÉRATION DE LA MAC ET DU NOM D'HÔTE
# ============================================================

def get_mac(ip: str) -> str:
    """
    Récupère la MAC d'une IP via `ip neigh` ou `arp -n`.
    """
    result = subprocess.run(
        ["ip", "neigh", "show", ip],
        capture_output=True, text=True
    )
    m = re.search(r"lladdr\s+([0-9a-f:]{17})", result.stdout)
    if m:
        return m.group(1)

    result = subprocess.run(
        ["arp", "-n", ip],
        capture_output=True, text=True
    )
    m = re.search(r"([0-9a-f]{2}(?::[0-9a-f]{2}){5})", result.stdout)
    return m.group(1) if m else ""


def get_hostname(ip: str) -> str:
    """
    Résolution DNS inverse, puis fallback NetBIOS via nmblookup.
    """
    try:
        socket.setdefaulttimeout(1.0)
        name, _, _ = socket.gethostbyaddr(ip)
        if name:
            return name
    except (socket.herror, socket.gaierror, socket.timeout, OSError):
        pass

    try:
        result = subprocess.run(
            ["nmblookup", "-A", ip],
            capture_output=True, text=True, timeout=2
        )
        m = re.search(r"^\s+(\S+)\s+<00>\s+UNIQUE", result.stdout, re.M)
        if m:
            return m.group(1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return ""


def get_vendor(mac: str) -> str:
    """
    Identifie le constructeur depuis le préfixe MAC (OUI).
    """
    if not mac:
        return ""
    oui_file = Path("/usr/share/arp-scan/ieee-oui.txt")
    if not oui_file.exists():
        return ""
    prefix = mac[:8].upper().replace(":", "")
    try:
        with open(oui_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith(prefix):
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        return parts[1]
    except PermissionError:
        return ""
    return ""


# ============================================================
# 4. AFFICHAGE ET SAUVEGARDE
# ============================================================

def render_table(hosts: list[dict]) -> str:
    lines = []
    lines.append("=" * 90)
    lines.append(f"Scan LAN — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 90)
    lines.append(f"{'IP':<18} {'MAC':<20} {'NOM':<28} {'CONSTRUCTEUR':<20}")
    lines.append("-" * 90)
    for h in hosts:
        lines.append(
            f"{h['ip']:<18} {h['mac'] or '-':<20} "
            f"{h['hostname'] or '-':<28} {h['vendor'] or '-':<20}"
        )
    lines.append("=" * 90)
    lines.append(f"{len(hosts)} machine(s) vivante(s)")
    return "\n".join(lines)


def save_results(hosts: list[dict], network: str, iface: str):
    out_dir = Path("scans")
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    payload = {
        "scanned_at": datetime.now().isoformat(),
        "network": network,
        "interface": iface,
        "hosts": hosts,
    }

    json_path = out_dir / f"scan_{stamp}.json"
    txt_path  = out_dir / f"scan_{stamp}.txt"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(render_table(hosts))

    # si lancé via sudo, redonne la propriété à l'utilisateur appelant
    uid = int(os.environ.get("SUDO_UID", os.getuid()))
    gid = int(os.environ.get("SUDO_GID", os.getgid()))
    try:
        os.chown(out_dir, uid, gid)
        for p in (json_path, txt_path):
            os.chown(p, uid, gid)
    except PermissionError:
        pass

    return json_path, txt_path


# ============================================================
# 5. PROGRAMME PRINCIPAL
# ============================================================

def main():
    if not sys.platform.startswith("linux"):
        print("[!] Ce script est prévu pour Linux (Kali).")
        sys.exit(1)

    print("[*] Détection du réseau local...")
    network, iface = get_local_network()
    print(f"    Interface : {iface}")
    print(f"    Réseau    : {network}")

    print(f"[*] Scan nmap sur {network} (peut prendre 15-30 s)...")
    alive = nmap_discover(network)
    print(f"    {len(alive)} machine(s) répondent")

    if not alive:
        print("[!] Aucune machine trouvée. La cible est peut-être éteinte.")
        return

    print("[*] Récupération MAC / nom / constructeur...")
    hosts = []
    for ip in alive:
        mac = get_mac(ip)
        name = get_hostname(ip)
        vendor = get_vendor(mac)
        hosts.append({"ip": ip, "mac": mac, "hostname": name, "vendor": vendor})
        print(f"    {ip:<18} {mac or '-':<20} {name or '-':<28} {vendor or '-'}")

    print()
    print(render_table(hosts))

    json_path, txt_path = save_results(hosts, network, iface)
    print(f"[+] Résultats sauvegardés :")
    print(f"    {json_path}")
    print(f"    {txt_path}")


if __name__ == "__main__":
    main()
