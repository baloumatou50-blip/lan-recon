#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
    echo "[!] Lance ce script avec sudo :  sudo ./install.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/lan_recon.py"

if [[ ! -f "$SRC" ]]; then
    echo "[!] Fichier lan_recon.py introuvable à côté de install.sh"
    exit 1
fi

echo "[*] Installation des dépendances système..."
apt update
apt install -y nmap samba-common-bin arp-scan python3

echo "[*] Copie de l'outil dans /usr/local/bin/lan-recon..."
install -m 0755 "$SRC" /usr/local/bin/lan-recon
ln -sf /usr/local/bin/lan-recon /usr/bin/lan-recon

echo "[*] Rendre la base OUI lisible (facultatif)..."
if [[ -f /usr/share/arp-scan/ieee-oui.txt ]]; then
    chmod +r /usr/share/arp-scan/ieee-oui.txt || true
fi

echo ""
echo "[+] Installation terminée."
echo "    Lance l'outil avec :  sudo lan-recon"
