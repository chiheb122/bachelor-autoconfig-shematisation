# Dockerfile pour bachelor-autoconfig-shematisation
FROM python:3.9-slim

# Installer dépendances système pour pybind11, port série, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libudev-dev \
    usbutils \
    libcrypto++-dev \
    zlib1g-dev \
    git \
    minicom \
    && rm -rf /var/lib/apt/lists/*

# Créer le dossier de travail
WORKDIR /app

# Copier tous les fichiers du projet
COPY . .

# Installer dépendances Python
RUN pip install --upgrade pip
RUN pip install pyserial setuptools wheel pybind11

# Compilation du module natif
WORKDIR /app/lib/pka2xml_py
RUN bash build.sh

# Renommer la bibliothèque compilée pour que l'import Python fonctionne
RUN cp build/lib.linux-x86_64-3.9/pka2core.cpython-39-x86_64-linux-gnu.so ../pka2core.cpython-39-x86_64-linux-gnu.so

# Revenir au dossier de base
WORKDIR /app

# Installer les dépendances Python du projet
RUN pip install -r requirements.txt

# Point d'entrée interactif par défaut
CMD ["python3", "-m", "src.main"]
