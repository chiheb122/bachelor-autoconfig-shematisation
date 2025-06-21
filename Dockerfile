# Dockerfile
FROM python:3.11-slim

# Installation des outils nécessaires à la compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libstdc++-dev \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Création du dossier de travail
WORKDIR /app

# Copie des fichiers dans le conteneur
COPY lib/pka2xml_py .

# Installation des dépendances Python
RUN pip install --upgrade pip && pip install pybind11 setuptools wheel

# Compilation automatique lors du build (optionnel)
RUN ./build.sh

# Point d'entrée interactif par défaut
CMD [ "bash" ]
