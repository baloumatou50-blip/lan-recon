# lan-recon

Outil Python de découverte de réseau local.
Détecte automatiquement la plage réseau, scanne les machines vivantes,
récupère IP, MAC, nom d'hôte et constructeur. Sauvegarde en JSON et TXT.

## Prérequis

- Linux (testé sur Kali Linux)
- Python 3.10 ou plus
- Les droits `sudo`

Les dépendances système (`nmap`, `samba-common-bin`, `arp-scan`, `python3`)
sont installées automatiquement par `install.sh`.

## Installation

    git clone https://github.com/baloumatou50-blip/lan-recon.git
    cd lan-recon
    chmod +x install.sh
    sudo ./install.sh

L'installation :

1. installe les dépendances système via `apt`
2. copie l'outil dans `/usr/local/bin/lan-recon`
3. crée un lien symbolique dans `/usr/bin/lan-recon` (pour que `sudo` le trouve)
4. rend la base OUI lisible (pour l'affichage du constructeur)

Après ça, l'outil est disponible partout sous le nom `lan-recon`.

## Utilisation

    sudo lan-recon

L'outil détecte automatiquement ton interface réseau et ta plage locale,
scanne toutes les machines vivantes, puis affiche un tableau avec :

- l'adresse IP
- l'adresse MAC
- le nom d'hôte (DNS inverse ou NetBIOS)
- le constructeur (depuis le préfixe MAC)

Exemple de sortie (IP et noms volontairement anonymisés) :

    ==========================================================================================
    Scan LAN — 2026-09-25 13:42:21
    ==========================================================================================
    IP                 MAC                  NOM                          CONSTRUCTEUR
    ------------------------------------------------------------------------------------------
    192.168.1.*      aa:bb:cc:dd:ee:01    router.local                 -
    192.168.1.**      -                    host-a.local                 -
    192.168.1.**      -                    host-b.local                 -
    192.168.1.**      -                    host-c.local                 -
    ==========================================================================================
    4 machine(s) vivante(s)

## Sortie

À chaque exécution, deux fichiers sont créés dans `scans/` (dans le
dossier où tu lances la commande) :

- `scan_YYYYMMDD_HHMMSS.json` — format structuré, réutilisable
- `scan_YYYYMMDD_HHMMSS.txt` — version lisible du tableau

## Mise à jour

    cd lan-recon
    git pull
    chmod +x install.sh
    sudo ./install.sh

## Désinstallation

    sudo rm /usr/local/bin/lan-recon
    sudo rm /usr/bin/lan-recon

## Dépannage

### `sudo: ./install.sh : commande introuvable`

Le fichier `install.sh` n'a pas le bit exécutable après un `git clone`.
Corrige avec :

    chmod +x install.sh

### `sudo: lan-recon : commande introuvable` après l'installation

Sur certaines distributions, `sudo` utilise un `secure_path` qui
n'inclut pas `/usr/local/bin`. `install.sh` crée normalement un lien
symbolique dans `/usr/bin` pour contourner ce problème. Si ce n'est pas
le cas, crée-le manuellement :

    sudo ln -sf /usr/local/bin/lan-recon /usr/bin/lan-recon

### Les noms d'hôte des machines Windows n'apparaissent pas

L'outil utilise `nmblookup` (paquet `samba-common-bin`) pour résoudre
les noms NetBIOS. Vérifie qu'il est installé :

    sudo apt install samba-common-bin

### Pas de constructeur affiché, seulement `-`

La base OUI (`/usr/share/arp-scan/ieee-oui.txt`) n'est pas lisible.
Corrige avec :

    sudo chmod +r /usr/share/arp-scan/ieee-oui.txt

### Les fichiers dans `scans/` appartiennent à root

Corrigé dans la version actuelle : `save_results` réattribue les fichiers
à l'utilisateur qui a lancé la commande via `SUDO_UID`.

## Licence

MIT
