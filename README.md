# 🧠 Bachelor – Autoconfig & Schématisation réseau

Ce projet a été réalisé dans le cadre de mon travail de Bachelor. Il vise à automatiser la création de topologies réseau dans Cisco Packet Tracer à partir de fichiers de configuration au format JSON.

## 🎯 Objectif

- Générer automatiquement une topologie réseau (routeurs, switches, connexions) dans Packet Tracer
- Proposer une solution portable fonctionnant sur toute machine avec Packet Tracer installé

## 🛠️ Technologies

- Python 3
- Cisco Packet Tracer 8.2.2
- JSON (définition de topologie)

## 📁 Structure du projet

```
configExtract/
├── config/                   # Fichiers de configuration des équipements (txt)
├── models/                   # Modèles Python : Device, Router, Switch, Interface, Link, etc.
│   ├── Device.py
│   ├── Router.py
│   ├── Switch.py
│   ├── Interface.py
│   ├── Link.py
│   └── factory/
│       └── DeviceFactory.py
├── resources/
│   └── xml/                  # Templates XML pour Packet Tracer
│       ├── empty.xml
│       ├── router.xml
│       ├── switch.xml
│       └── link.xml
├── topologie/
│   ├── converter/
│   │   └── parser_config.py  # Parsing des configs et CDP
│   └── draw/
│       └── PktBuilder.py     # Génération du fichier XML final
├── main.py                   # Script principal
└── README.md                 # Documentation
```




