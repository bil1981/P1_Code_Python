# syntax=docker/dockerfile:1

# ============================================================
# 1. IMAGE DE BASE
# ============================================================
# Python 3.12, cohérent avec ton environnement local.
FROM python:3.12-slim

# ============================================================
# 2. VARIABLES D'ENVIRONNEMENT
# ============================================================
# Empêche Python de créer des fichiers .pyc.
ENV PYTHONDONTWRITEBYTECODE=1

# Affiche immédiatement les logs Python dans Docker.
ENV PYTHONUNBUFFERED=1

# Installation de uv dans le PATH.
ENV PATH="/root/.local/bin:$PATH"

# ============================================================
# 3. RÉPERTOIRE DE TRAVAIL
# ============================================================
WORKDIR /app

# ============================================================
# 4. INSTALLATION DE UV
# ============================================================
# uv permet d'installer les dépendances Python rapidement.
RUN pip install --no-cache-dir uv

# ============================================================
# 5. INSTALLATION DES DÉPENDANCES
# ============================================================
# IMPORTANT :
# requirements.txt est copié AVANT le code source.
#
# Cela permet à Docker de conserver cette couche en cache
# si seul le code Python est modifié.
COPY requirements.txt .

RUN uv pip install \
    --system \
    --no-cache \
    -r requirements.txt

# ============================================================
# 6. COPIE DU CODE DE L'APPLICATION
# ============================================================
# Cette instruction arrive après les dépendances afin
# d'optimiser le cache Docker.
COPY . .

# ============================================================
# 7. PORT DE L'APPLICATION
# ============================================================
# FastAPI/Uvicorn écoutera sur le port 8000.
EXPOSE 8000

# ============================================================
# 8. LANCEMENT DE L'APPLICATION
# ============================================================
# IMPORTANT :
# Remplacer main:app si ton fichier FastAPI porte un autre nom.
#
# Exemple :
# app.py  -> app:app
# main.py -> main:app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]