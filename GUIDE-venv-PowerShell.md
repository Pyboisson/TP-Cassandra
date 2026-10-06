# Guide — Utiliser le virtualenv (.venv) sous PowerShell

Ce guide explique comment:
- activer le virtualenv (.venv) dans une nouvelle fenêtre PowerShell,
- contourner la politique d’exécution de scripts Windows si elle bloque l’activation,
- désactiver le virtualenv.

Chemin du projet:
- `C:\Users\boiss\Desktop\Données distribuées\seance-02\TP_jour2`
- Virtualenv gardé: `.venv` (dans le dossier du projet)

---

## 1) Activer le .venv dans PowerShell

Copiez/collez ces commandes dans une nouvelle fenêtre PowerShell:

```powershell
Set-Location -Path "C:\Users\boiss\Desktop\Données distribuées\seance-02\TP_jour2"
# (optionnel mais recommandé) autorise l'exécution de scripts pour cette session uniquement
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Active le virtualenv (.venv)
. ".\.venv\Scripts\Activate.ps1"

# Vérifications utiles
python --version
Get-Command python
python -m pip list
```

Vous devriez voir le prompt PowerShell commencer par `(.venv)` et `Get-Command python` pointer vers `.venv\Scripts\python.exe`.

---

## 2) Installer / mettre à jour les dépendances

Dans le .venv actif:

```powershell
python -m pip install --upgrade pip
# installer à partir du fichier requirements.txt exporté
pip install -r .\requirements.txt

# ou, si besoin spécifique
pip install requests cassandra-driver
```

---

## 3) Lancer votre script Python

Toujours dans le .venv actif:

```powershell
python .\script\getapi.py
```

---

## 4) Sortir / désactiver le .venv

Pour revenir à l'environnement système Python:

```powershell
deactivate
```

Alternative explicite:

```powershell
& ".\.venv\Scripts\Deactivate.ps1"
```

Fermer la fenêtre PowerShell désactive également le .venv pour la prochaine session.

---

## 5) Dépannage rapide

- Erreur « scripts désactivés » ou « running scripts is disabled on this system »:
  - Utilisez `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` AVANT l'activation.
  - Cela ne modifie la politique que pour la session courante (sécurité conservée).

- `python` ne semble pas venir du .venv après activation:
  - Vérifiez votre commande d'activation: `. ".\.venv\Scripts\Activate.ps1"` (notez le point et l’espace au début pour dot-sourcer).
  - Vérifiez `Get-Command python` pour voir le chemin.

- Problèmes de paquets manquants:
  - Assurez-vous que vous installez dans le bon environnement (après activation).
  - `python -m pip install <paquet>` garantit l’installation via le Python actif.

- Mettre à jour pip si nécessaire:
  - `python -m pip install --upgrade pip`

---

## 6) Raccourcis pratiques

- Ouvrir rapidement une fenêtre PowerShell avec .venv activé (fichier fourni):
  - Double-cliquez: `Open-Venv-PowerShell.cmd` à la racine du projet.

- Dans VS Code, ouvrir un terminal avec .venv activé (tâche fournie):
  - Terminal → Run Task… → `Open venv shell`

---

Dernière mise à jour: généré automatiquement par l'assistant.
