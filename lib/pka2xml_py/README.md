# 🔐 pka2xml_py

> 🧠 Décrypte et recrypte les fichiers `.pkt` / `.pka` de Cisco Packet Tracer – en Python, via un module C++ compilé.

---

## 🚀 Objectif

Ce projet permet d’analyser et de modifier des fichiers `.pkt` ou `.pka` en les **convertissant en XML**, puis en les **recryptant** après modification.

- ✅ Décryptage de topologie `.pkt` en `.xml`
- ✅ Recryptage du fichier `.xml` modifié vers un `.pkt` utilisable par Packet Tracer
- ✅ Cross-plateforme : fonctionne sur macOS, Linux, Windows
- ✅ Compilation automatique du module natif avec `pybind11`

---

## 📦 Prérequis

- **Python 3.9+**
- **CMake**
- **Compilateur C++17** (GCC/Clang/MSVC)
- **pybind11** (installé automatiquement)

---

## 🛠️ Installation

### 1. Cloner le dépôt

```bash
git clone 
cd pka2xml_py
```


▶️ Sur macOS / Linux
```bash

chmod +x build.sh
./build.sh
```

🪟 Sur Windows

Ouvre PowerShell ou Git Bash :
```bash

build.bat
```


🔧 Commandes

```bash

python3 cli.py decrypt path/to/input.pkt path/to/output.xml
```


```bash

python3 cli.py decrypt tests/2.pkt output/topology.xml
```

🔐 Recrypter un fichier XML vers un .pkt
```bash

python3 cli.py encrypt path/to/input.xml path/to/output.pkt
```

Exemple :


python3 cli.py encrypt output/topology.xml rebuilt.pkt

Déobfuscation
Déchiffrement (Twofish, EAX)
Décompression (Zlib)
→ 🧾 XML lisible
L’opération inverse est utilisée pour re-générer un fichier .pkt.

📁 Arborescence du projet
```bash

pka2xml_py/
├── cpp_binding/           # Code C++ (pybind11)
│   ├── bindings.cpp
│   ├── include/pka2xml.hpp
├── pka2core/              # Module Python
│   └── __init__.py
├── cli.py                 # Interface ligne de commande
├── build.sh               # Build pour macOS/Linux
├── build.bat              # Build pour Windows
├── setup.py               # Build Python setuptools
└── README.md              # Documentation
```


🔒 Avertissement

Ce projet est à but éducatif. L’ingénierie inverse de Packet Tracer peut violer ses conditions d’utilisation. Utilisez-le de façon responsable et uniquement sur vos propres fichiers.

💡 Auteur

👨‍💻 Projet initié par Chiheb
🔗 Basé sur ferib.dev