# Déployer ce fork

Ce dépôt contient un moteur FastAPI (backend) + une interface web statique
(`frontend/`, servie par le même processus sous `/ui/`). Une seule commande
suffit à faire tourner les deux ensemble.

## 1. Avant toute mise en ligne publique — obligation légale (AGPL-3.0 §13)

Lisez `CHANGES.md`. En résumé : ce fork ne doit pas être exposé sur un site
public tant que (a) son code n'est pas lui-même publié sur un dépôt public
(GitHub/GitLab...) et (b) le lien vers ce dépôt n'a pas été renseigné dans
`frontend/index.html` (chercher `__LIEN_DEPOT_PUBLIC_A_COMPLETER__`). Ce n'est
pas une formalité : c'est la condition légale d'usage de la licence.

## 2. Tester en local

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --reload
# API : http://localhost:8000/docs
# Interface : http://localhost:8000/ui/
```

## 3. Déployer avec Docker (n'importe quel hébergeur qui accepte un conteneur)

```bash
docker build -t francebudget-fork .
docker run -p 8000:8000 -e CORS_ORIGINS=https://votre-domaine.fr francebudget-fork
```

## 4. Options d'hébergement (aucune n'est requise par ce projet — à choisir selon budget/préférence)

- **Render / Railway / Fly.io** : détectent le `Dockerfile` automatiquement,
  offre gratuite ou quelques dollars/mois, le plus simple pour un premier
  déploiement public sans gérer de serveur.
- **VPS (OVH, Hetzner, Scaleway...)** : `docker run` directement, ou un
  service systemd qui lance `uvicorn` ; nécessite de gérer soi-même le
  certificat HTTPS (ex. via Caddy ou Nginx + Let's Encrypt en reverse proxy).
- **Auto-hébergement local** : suffisant pour un usage interne/privé (pas
  d'obligation de publication du code tant que le service n'est pas exposé
  à des tiers sur un réseau — voir CHANGES.md).

## 5. Variables d'environnement utiles

| Variable | Défaut | Rôle |
|---|---|---|
| `CORS_ORIGINS` | localhost uniquement | domaines autorisés à appeler l'API depuis un navigateur (CSV) |
| `DEBUG_MODE` | `false` | `true` = messages d'erreur détaillés + logs de simulation dans la réponse (à NE PAS activer en prod publique) |
| `API_PORT` | `8000` | port d'écoute |

## 6. Après déploiement

- Vérifier `GET /health` retourne `{"status":"healthy"}`.
- Vérifier `GET /ui/` charge l'interface et qu'un levier (ex. TVA) met bien à
  jour le graphique par décile.
- Mettre à jour le lien "Code source" dans `frontend/index.html` (voir §1).
