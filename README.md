# lan-recon

Outil Python de découverte de réseau local.
Détecte automatiquement la plage réseau, scanne les machines vivantes,
récupère IP, MAC, nom d'hôte et constructeur. Sauvegarde en JSON et TXT.

## Installation

    git clone https://github.com/baloumatou50-blip/lan-recon.git
    cd lan-recon
    sudo ./install.sh

Après ça, l'outil est disponible partout sous le nom `lan-recon`.

## Utilisation

    sudo lan-recon

## Sortie

- Tableau lisible dans le terminal
- Sauvegarde dans `scans/scan_YYYYMMDD_HHMMSS.json` et `.txt`

## Désinstallation

    sudo rm /usr/local/bin/lan-recon

## Licence

MIT
