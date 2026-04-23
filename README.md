# 🖱️ MX Master Hyprland Workspace Switcher

> Switcher de workspaces gestuel pour Hyprland avec le bouton pouce de la Logitech MX Master 3/3S/3B.  
> Maintenir le bouton pouce + glisser gauche/droite pour naviguer vers des **workspaces vides** — indépendamment sur chaque moniteur.

![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?style=flat&logo=arch-linux&logoColor=white)
![Hyprland](https://img.shields.io/badge/Hyprland-58E1FF?style=flat&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/Licence-MIT-green?style=flat)

---

⚠️ Avertissement

Ce script est en version bêta. Il peut contenir des bugs, notamment sur des configurations multi-moniteurs non testées.
N'hésite pas à ouvrir une issue ou une pull request si tu rencontres un problème ! 🙏

---

## ✨ Fonctionnalités

- 🖱️ **Maintenir le bouton pouce + glisser** gauche ou droite pour changer de workspace
- 🖥️ **Support multi-moniteur** — chaque écran navigue indépendamment
- 🆕 **Crée automatiquement des workspaces vides** — n'atterrit jamais sur un workspace occupé
- ⏪ **Historique de navigation** par moniteur — glisser en arrière pour revenir aux workspaces précédents
- 🔒 **Zéro interférence entre moniteurs** — les workspaces sont totalement isolés par écran
- 🚀 **Démarrage automatique** via Hyprland `exec-once`

---

## 📋 Prérequis

- Arch Linux (ou toute distro basée sur Arch)
- [Hyprland](https://hyprland.org/)
- Python 3.10+
- `python-evdev`
- Logitech MX Master 3 / 3S / 3 for Business (récepteur USB ou Bluetooth)

---

## ⚡ Installation

### 1. Installer les dépendances

```bash
sudo pacman -S python-pip
pip install evdev --break-system-packages
```

### 2. Ajouter ton utilisateur au groupe `input`

```bash
sudo usermod -aG input $USER
```

> ⚠️ Déconnecte-toi et reconnecte-toi pour que le changement soit pris en compte.

### 3. Trouver le chemin de ta souris

```bash
sudo evtest
```

Repère `Logitech USB Receiver Mouse` et note son numéro d'événement (ex : `event9`).

### 4. Cloner et installer

```bash
git clone https://github.com/RgGeoIII/mx-master-hyprland.git
cd mx-master-hyprland
mkdir -p ~/.local/bin
cp mx_workspace.py ~/.local/bin/mx_workspace.py
chmod +x ~/.local/bin/mx_workspace.py
```

### 5. Configurer le chemin du périphérique

Édite `~/.local/bin/mx_workspace.py` et modifie la variable `DEVICE_PATH` :

```python
DEVICE_PATH = "/dev/input/event9"  # ← à adapter selon ton système
```

### 6. Démarrage automatique avec Hyprland

Ajoute la ligne `exec-once` dans `~/.config/hypr/hyprland.conf` :

```bash
echo "exec-once = python3 ~/.local/bin/mx_workspace.py" >> ~/.config/hypr/hyprland.conf
```

Vérifie que la ligne a bien été ajoutée :

```bash
grep exec-once ~/.config/hypr/hyprland.conf
```

Recharge Hyprland pour appliquer :

```bash
hyprctl reload
```

---

## 🎮 Utilisation

| Geste | Action |
|-------|--------|
| Maintenir bouton pouce + glisser **droite** | Aller au prochain workspace vide |
| Maintenir bouton pouce + glisser **gauche** | Revenir au workspace précédent dans l'historique |

---

## ⚙️ Configuration

En haut du fichier `mx_workspace.py` :

```python
DEVICE_PATH = "/dev/input/event9"  # Chemin vers ta souris
THRESHOLD   = 40                   # Distance de glissement avant de switcher (plus bas = plus sensible)
COOLDOWN    = 0.5                  # Secondes entre deux switchs
```

---

## 🐛 Dépannage

**Le script ne détecte pas la souris**
```bash
sudo evtest  # Vérifie ton chemin de périphérique
```

**Permission refusée**
```bash
sudo usermod -aG input $USER
# Puis déconnecte-toi et reconnecte-toi
```

**Mauvais moniteur qui switche**
Assure-toi que `DEVICE_PATH` pointe vers l'entrée **Mouse** et non `Consumer Control` ou `System Control`.

---

## 🗺️ Feuille de route

- [ ] Détection automatique du chemin du périphérique
- [ ] Fichier de configuration (`~/.config/mx-workspace/config.toml`)
- [ ] Support de la MX Master 2S
- [ ] Paquet AUR

---

## 📄 Licence

MIT © 2026 — Fait avec ❤️ sur Arch Linux
