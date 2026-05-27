# Guide de Déploiement Luthor sur Google Cloud Run

## Prérequis

Avant de commencer, assurez-vous d'avoir :
- Un compte Google Cloud avec billing activé
- Google Cloud CLI (`gcloud`) installé sur votre machine
- Docker installé localement
- Accès à votre domaine Luthor.org via Spacesquare

## Informations de Déploiement

| Paramètre | Valeur |
|-----------|--------|
| **Project Name** | LUTHOR WM |
| **Project ID** | project-85dac716-4594-4638-805 |
| **Project Number** | 666243405118 |
| **Region** | europe-west1 (Paris) |
| **Service Name** | luthor |
| **Domain** | luthor.org |

## Étape 1 : Configuration Initiale

Authentifiez-vous auprès de Google Cloud et définissez le projet par défaut :

```bash
gcloud auth login
gcloud config set project project-85dac716-4594-4638-805
gcloud auth configure-docker gcr.io
```

## Étape 2 : Activation des Services Nécessaires

Activez les APIs Cloud Build et Cloud Run :

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Étape 3 : Déploiement via Cloud Build

Le déploiement automatique se fait via Cloud Build. Poussez simplement votre code sur GitHub et configurez Cloud Build pour déclencher automatiquement le déploiement :

```bash
# Depuis votre dépôt GitHub, configurez Cloud Build
gcloud builds connect --repository-name=LuThoR --repository-owner=ChawnRob --region=europe-west1
```

Ou déployez manuellement :

```bash
gcloud builds submit --config=cloudbuild.yaml
```

## Étape 4 : Configuration du Domaine Personnalisé

Une fois le service déployé sur Cloud Run, configurez votre domaine Luthor.org :

### 4.1 Obtenez l'URL Cloud Run

```bash
gcloud run services describe luthor --region=europe-west1 --format='value(status.url)'
```

Vous obtiendrez une URL comme : `https://luthor-xxxxx-ew.a.run.app`

### 4.2 Configurez le Domaine Personnalisé

Dans la console Cloud Run, allez à **Services > luthor > Manage Custom Domains** et ajoutez `luthor.org`.

### 4.3 Configurez le DNS chez Spacesquare

Chez votre registraire Spacesquare, configurez les enregistrements DNS suivants :

**Pour un sous-domaine (recommandé) :**
- Type : CNAME
- Nom : @ (ou laissez vide pour la racine)
- Valeur : `ghs.googledomains.com`

Ou utilisez les enregistrements A fournis par Google Cloud.

## Étape 5 : Vérification du Déploiement

Vérifiez que votre service est en ligne :

```bash
# Vérifiez le statut du service
gcloud run services describe luthor --region=europe-west1

# Consultez les logs
gcloud run services logs read luthor --region=europe-west1 --limit=50
```

Accédez à votre site :
- Version française : https://luthor.org/fr
- Version anglaise : https://luthor.org/en
- Version par défaut : https://luthor.org

## Étape 6 : Configuration du Certificat SSL

Google Cloud Run fournit automatiquement un certificat SSL pour votre domaine personnalisé. Vérifiez que le certificat est valide :

```bash
# Vérifiez les certificats
gcloud compute ssl-certificates list
```

## Optimisation et Monitoring

### Surveillance des Performances

Consultez les métriques Cloud Run :

```bash
gcloud monitoring dashboards list
```

### Mise à l'Échelle Automatique

Cloud Run met automatiquement à l'échelle votre service. Les paramètres actuels sont :
- **Mémoire** : 512 Mo
- **CPU** : 1 vCPU
- **Timeout** : 3600 secondes
- **Concurrence** : 80 (par défaut)

### Réduction des Coûts

Pour réduire les coûts :
- Utilisez **Cloud Run on Compute Engine** pour les workloads stables
- Configurez **Cloud CDN** pour mettre en cache les assets statiques
- Utilisez **Cloud Armor** pour protéger contre les attaques DDoS

## Dépannage

### Le service ne démarre pas

Consultez les logs :
```bash
gcloud run services logs read luthor --region=europe-west1 --limit=100
```

### Le domaine personnalisé ne fonctionne pas

Vérifiez la propagation DNS :
```bash
nslookup luthor.org
dig luthor.org
```

### Les performances sont lentes

Vérifiez les métriques Cloud Run et augmentez la mémoire/CPU si nécessaire.

## Mise à Jour du Code

Pour mettre à jour votre code :

1. Poussez vos changements sur GitHub
2. Cloud Build déclenche automatiquement un nouveau déploiement
3. Cloud Run remplace l'ancienne version par la nouvelle

## Support et Documentation

- [Documentation Cloud Run](https://cloud.google.com/run/docs)
- [Guide des Domaines Personnalisés](https://cloud.google.com/run/docs/mapping-custom-domains)
- [Tarification Cloud Run](https://cloud.google.com/run/pricing)

---

**Déployé par Manus AI** | **Date** : Mai 2026
