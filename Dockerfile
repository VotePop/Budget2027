# Dockerfile — moteur france-budget-simulateur (fork) + extension décile + UI.
# AGPL-3.0. Voir CHANGES.md pour l'obligation de publication du code source
# (§13) avant toute mise en ligne publique.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV API_HOST=0.0.0.0
ENV API_PORT=8000
# CORS_ORIGINS : à surcharger avec le(s) domaine(s) publique(s) réel(s) en prod,
# ex. -e CORS_ORIGINS=https://mon-domaine.fr
ENV DEBUG_MODE=false

EXPOSE 8000

# healthcheck simple, réutilise l'endpoint /health déjà exposé par l'API
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
