# lan-recon

Outil Python de découverte de réseau local.
Détecte automatiquement la plage réseau, scanne les machines vivantes,
récupère IP, MAC, nom d'hôte et constructeur. Sauvegarde en JSON et TXT.

## Installation

    sudo apt update
    sudo apt install -y nmap samba-common-bin
    sudo chmod +r /usr/share/arp-scan/ieee-oui.txt

## Utilisation

    sudo python3 lan_recon.py

## Sortie

- Affichage tableau dans le terminal
- Sauvegarde dans `scans/scan_YYYYMMDD_HHMMSS.json` et `.txt`

## Licence

MIT
