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
