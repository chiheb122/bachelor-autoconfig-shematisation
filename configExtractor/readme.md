### ========================================
## Script d'extraction de configuration Cisco
### ========================================

📌 Objectif :

Ce script permet de se connecter automatiquement à un appareil Cisco (switch ou routeur) via un **câble console** (port série), d’**extraire la configuration complète** (`show running-config`), de la nettoyer, puis de l’enregistrer dans un **fichier texte structuré**, placé dans un dossier par réseau.

---

🧰 Fonctionnalités :
- Détection automatique du port COM utilisé
- Authentification avec mot de passe console et enable (saisie personnalisée possible)
- Identification automatique du type d’équipement : **switch ou routeur**
- Extraction de la configuration complète (`show running-config`)
- Nettoyage des entêtes et des lignes inutiles
- Enregistrement des fichiers dans `config/<nom_du_réseau>/`
- Compatible **Windows / Linux / macOS**

---

📁 Structure de sortie :

Les fichiers sont enregistrés dans un sous-dossier au choix :
```
Exemple :
config/
└── reseau1/
    ├── switch_config.txt
    └── router_config.txt
```
---

🚀 Instructions d'utilisation :

1. Branche ton câble console USB-RJ45 à ton PC et à ton appareil Cisco
2. Lancer le script Python :
   python pytermi.py
3. Suis les étapes interactives :
   - Saisie des mots de passe (ou utilisation des valeurs par défaut)
   - Saisie du nom du sous-dossier de réseau (`reseau1`, `batimentA`, etc.)
4. Le script détecte le port série, s’y connecte, extrait la configuration, et l’enregistre.

---

⚙️ Mots de passe par défaut :
- Console : `cisco`
- Enable : `class`

Vous pouvez les modifier à l’exécution ou dans le script si vous le souhaitez.

---

💡 Astuce Linux :
Sur Linux, pour autoriser l’accès au port série sans `sudo`, exécute :
```bash
   sudo usermod -aG dialout $USER
   ```
Puis **déconnectez-vous / reconnectez-vous**.

---

👨‍💻 Dépendances :
Installez les dépendances avec :
```bash
   pip install pyserial
   ```

---

📂 Organisation recommandée du projet :
```
bachelor-autoconfig-shematisation/
├── config/                ← Dossier de sortie pour les fichiers
├── configExtractor/
│   └── pytermi.py         ← Script principal
```
---


Projet de Bachelor – HEG Genève – 2025