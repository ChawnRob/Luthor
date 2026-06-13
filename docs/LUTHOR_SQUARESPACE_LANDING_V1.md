# LUTHOR — Landing Page V1 (Vitrine Squarespace)

> **But de ce document** : fournir une proposition complète (structure, contenu prêt à copier-coller, direction visuelle, checklist) pour construire la **landing page V1 de `luthor.org` dans Squarespace**.
>
> **Périmètre** : ce document ne concerne **que la vitrine marketing**. Il ne touche ni au backend, ni au modèle JEPA, ni aux providers LLM, ni au déploiement Cloud Run, ni à l'architecture Python.
>
> **Statut produit à communiquer** : LUTHOR est un **projet en construction avancée** (prototype + R&D), **pas** un produit fini. Aucune fonctionnalité ne doit être présentée comme « disponible en production » tant qu'elle ne l'est pas. On parle de **vision** et de **work in progress**, pas de promesses.

---

## 0. Principes directeurs

1. **Squarespace = vitrine principale** de `luthor.org`. Cloud Run reste réservé à la future application / API (`app.luthor.org`).
2. **Honnêteté** : on présente une vision claire (Agentic World Model : planning, mémoire, tâches autonomes) et l'état réel d'avancement (prototype open source, recherche en cours).
3. **Pas « chatbot »** : LUTHOR n'est pas un énième assistant conversationnel. On insiste sur le **modèle du monde**, la **planification** et l'**autonomie**.
4. **Pas de marketing creux** : pas de superlatifs vides, pas de chiffres de performance inventés, pas de « révolutionnaire » à toutes les lignes.
5. **Séparation stricte** : ce document parle **uniquement de LUTHOR**. **COCO / OpenChawn** ne doit pas apparaître sur cette vitrine.
6. **Recréable dans Squarespace** : chaque section correspond à un ou deux blocs Squarespace standards (Section, Text, Button, Card/Grid, Accordion).

---

## 1. Direction visuelle

Cohérente avec l'identité technique déjà esquissée pour le projet (style « Futuristic Minimalism »).

### Ambiance
- **Sombre, sobre, premium.** Beaucoup d'espace négatif, hiérarchie typographique forte.
- Esthétique « laboratoire d'IA » (proche de DeepMind / Anthropic), **pas** « SaaS coloré ».
- Un seul accent lumineux (cyan) utilisé avec parcimonie pour guider l'œil.

### Palette
| Rôle | Couleur | Hex |
| :--- | :--- | :--- |
| Fond principal | Charcoal profond | `#0F1419` |
| Texte principal | Blanc cassé | `#F4F6F8` |
| Texte secondaire | Gris clair | `#9AA4AF` |
| Accent primaire | Cyan électrique | `#00D9FF` |
| Accent secondaire | Indigo | `#6366F1` |
| Bordures / séparateurs | Gris très sombre | `#1E2630` |

> Dans Squarespace : définir ces couleurs dans **Design → Colors** (créer une palette « Luthor Dark ») et appliquer le thème sombre à toutes les sections.

### Typographie
- **Titres** : Poppins / Space Grotesk (Bold 700) — moderne, tech.
- **Corps** : Inter (Regular 400 / Medium 500) — lisible.
- **Détails techniques / labels** : Space Mono (pour les petits libellés type `// world model`, badges, légendes).

> Dans Squarespace : **Design → Fonts**, choisir une « Font Pack » avec une titre géométrique + un corps sans-serif lisible. Space Mono peut servir uniquement pour les badges/petits labels.

### Éléments graphiques
- Fond de hero : dégradé sombre + éventuellement une image abstraite (réseau de nœuds, latent space, lignes de connexion) en faible opacité (~20–30 %).
- Badges arrondis discrets (« En construction avancée », « Open source », « Inspiré de JEPA / LeCun »).
- Bordures fines cyan sur les cartes clés.
- Animations légères uniquement (fade-in au scroll). Pas d'effets criards.

---

## 2. Architecture de la page (ordre des sections)

Page unique (one-pager) en V1, scroll vertical :

1. **Hero** — accroche + sous-titre + CTA + badge « en construction »
2. **Proposition de valeur** — qu'est-ce que LUTHOR, en 3 phrases
3. **Ce qui rend LUTHOR différent** — modèle du monde vs génératif
4. **Sections principales (piliers)** — Planning · Memory · Autonomous Tasks · Efficience
5. **LUTHOR vs un chatbot classique** — tableau comparatif
6. **Roadmap / État d'avancement** — transparence sur le « work in progress »
7. **Fondements & inspiration** — JEPA, AMI, Yann LeCun (crédibilité)
8. **Call-to-action principal** — suivre / contribuer / rester informé
9. **Contact / GitHub / Footer**

> Anchors recommandés pour la navigation : `#vision`, `#difference`, `#piliers`, `#comparaison`, `#roadmap`, `#contact`.

---

## 3. Contenu prêt à copier-coller — 🇫🇷 Version Française

### 3.1 — Navigation (header)
- Logo : **Luthor**
- Liens : `Vision` · `Différence` · `Roadmap` · `GitHub`
- Bouton (optionnel, discret) : `Suivre le projet`

---

### 3.2 — Hero

**Badge (petit label au-dessus du titre) :**
```
Projet en construction avancée · Open source
```

**Titre (H1) :**
```
Un modèle du monde, pas un simple chatbot.
```

**Sous-titre :**
```
Luthor est un Agentic World Model : une IA conçue pour se représenter
son environnement, anticiper les conséquences de ses actions et planifier
pour atteindre un objectif — au lieu de seulement générer du texte.
```

**Bouton principal :**
```
Découvrir la vision
```
(lien → `#vision`)

**Bouton secondaire :**
```
Voir le code sur GitHub
```
(lien → `https://github.com/ChawnRob/Luthor`)

---

### 3.3 — Proposition de valeur (`#vision`)

**Titre (H2) :**
```
Comprendre. Anticiper. Agir.
```

**Paragraphe :**
```
La plupart des IA actuelles génèrent une réponse, un mot après l'autre.
Luthor explore une autre voie : apprendre une représentation abstraite du
monde pour raisonner et planifier dans cet espace, plutôt que de tout produire
sous forme de texte. L'objectif : des agents plus autonomes, plus cohérents
sur la durée, et plus économes en calcul.
```

> Note honnêteté : formulé comme une **direction de recherche** (« explore », « l'objectif »), pas comme un résultat acquis.

---

### 3.4 — Ce qui rend Luthor différent (`#difference`)

**Titre (H2) :**
```
Penser dans un espace latent
```

**Paragraphe :**
```
Le cœur de Luthor repose sur les principes de la Joint Embedding Predictive
Architecture (JEPA). Plutôt que de reconstruire chaque détail du futur, Luthor
prédit l'évolution du monde dans un espace de représentation abstrait. Il se
concentre sur ce qui est important pour décider — pas sur la forme littéraire
de la réponse.
```

---

### 3.5 — Sections principales / Piliers (`#piliers`)

**Titre (H2) :**
```
Les piliers de Luthor
```

**Carte 1 — Planning**
```
Planification
Luthor simule mentalement plusieurs futurs possibles, évalue chaque
trajectoire, puis choisit l'action qui rapproche le plus de l'objectif.
```

**Carte 2 — Memory**
```
Mémoire
Une représentation interne du contexte et de l'historique, pensée pour
raisonner sur le long terme sans tout regénérer à chaque étape.
```

**Carte 3 — Autonomous Tasks**
```
Tâches autonomes
L'ambition : des agents capables de décomposer un objectif en étapes et de
les exécuter de façon autonome, en se corrigeant en cours de route.
```

**Carte 4 — Efficience**
```
Efficience
Une architecture pensée pour réduire le coût de calcul : raisonner dans
l'espace latent plutôt que tout produire en texte.
```

> Note honnêteté : « L'ambition », « pensée pour » → on assume que c'est en cours.

---

### 3.6 — Luthor vs un chatbot classique (`#comparaison`)

**Titre (H2) :**
```
Luthor n'est pas un chatbot
```

**Tableau :**

| | Chatbot classique | Luthor (Agentic World Model) |
| :--- | :--- | :--- |
| Objectif | Générer une réponse | Atteindre un objectif |
| Méthode | Prédire le mot suivant | Prédire l'état futur du monde |
| Horizon | Une réponse à la fois | Planification sur plusieurs étapes |
| Mémoire | Limitée au contexte de la requête | Représentation interne persistante (visée) |
| Sortie | Du texte | Une décision / une action |

> Dans Squarespace : utiliser un **bloc Tableau (Markdown ou Table block)**, ou à défaut une grille de 2 colonnes.

---

### 3.7 — Roadmap / État d'avancement (`#roadmap`)

**Titre (H2) :**
```
Où en est Luthor
```

**Intro :**
```
Luthor est un projet en construction avancée. Voici, en toute transparence,
ce qui existe aujourd'hui et ce que nous construisons ensuite.
```

**Aujourd'hui (prototype) :**
```
— Prototype open source du modèle du monde (encodeur, prédicteur, planificateur)
— Boucle de planification par simulation de trajectoires (MPC)
— Documentation technique publique
```

**En cours :**
```
— Prédicteurs et encodeurs plus riches
— Mémoire long terme et horizons de planification étendus
— Infrastructure d'agents autonomes
```

**Ensuite :**
```
— Application et API dédiées (app.luthor.org)
— Environnements et tâches plus complexes
— Outils pour développeurs et intégrateurs
```

> Important : présenter ceci comme une **feuille de route**, pas comme des livraisons datées. Ne pas annoncer de dates.

---

### 3.8 — Fondements & inspiration

**Titre (H2) :**
```
Fondé sur la recherche
```

**Paragraphe :**
```
Luthor s'inspire des travaux sur l'Intelligence Machine Autonome (AMI) et la
Joint Embedding Predictive Architecture (JEPA) popularisés par Yann LeCun :
apprentissage auto-supervisé, modèles du monde non génératifs, et planification
guidée par un coût. Une base théorique solide pour construire des agents qui
raisonnent.
```

---

### 3.9 — Call-to-action principal

**Titre (H2) :**
```
Suivez la construction de Luthor
```

**Paragraphe :**
```
Le projet est ouvert et évolue rapidement. Explorez le code, suivez l'avancée,
ou prenez contact pour échanger sur le projet.
```

**Bouton principal :**
```
Explorer sur GitHub
```
(lien → `https://github.com/ChawnRob/Luthor`)

**Bouton secondaire :**
```
Nous contacter
```
(lien → `mailto:contact@luthor.org` — à ajuster selon l'adresse réelle)

---

### 3.10 — Footer / Contact (`#contact`)

```
Luthor — Agentic World Model
Un projet en construction avancée · Open source

GitHub : github.com/ChawnRob/Luthor
Contact : contact@luthor.org

© Luthor. Inspiré des principes AMI / JEPA.
```

---

## 4. Contenu prêt à copier-coller — 🇬🇧 English Version

### 4.1 — Navigation
- Logo: **Luthor**
- Links: `Vision` · `Difference` · `Roadmap` · `GitHub`
- Button (optional): `Follow the project`

---

### 4.2 — Hero

**Badge:**
```
Actively in development · Open source
```

**Title (H1):**
```
A world model, not just another chatbot.
```

**Subtitle:**
```
Luthor is an Agentic World Model: an AI designed to represent its environment,
anticipate the consequences of its actions, and plan toward a goal — instead of
just generating text.
```

**Primary button:**
```
Explore the vision
```
(link → `#vision`)

**Secondary button:**
```
View the code on GitHub
```
(link → `https://github.com/ChawnRob/Luthor`)

---

### 4.3 — Value proposition (`#vision`)

**Title (H2):**
```
Understand. Anticipate. Act.
```

**Paragraph:**
```
Most of today's AI generates an answer, one word at a time. Luthor explores a
different path: learning an abstract representation of the world to reason and
plan inside that space, rather than producing everything as text. The goal:
agents that are more autonomous, more coherent over time, and more
compute-efficient.
```

---

### 4.4 — What makes Luthor different (`#difference`)

**Title (H2):**
```
Thinking in latent space
```

**Paragraph:**
```
At its core, Luthor builds on the principles of the Joint Embedding Predictive
Architecture (JEPA). Rather than reconstructing every detail of the future,
Luthor predicts how the world evolves in an abstract representation space. It
focuses on what matters for making a decision — not on the literary form of an
answer.
```

---

### 4.5 — Core pillars (`#piliers`)

**Title (H2):**
```
The pillars of Luthor
```

**Card 1 — Planning**
```
Planning
Luthor mentally simulates several possible futures, scores each trajectory, and
picks the action that gets closest to the goal.
```

**Card 2 — Memory**
```
Memory
An internal representation of context and history, designed to reason over the
long term without regenerating everything at each step.
```

**Card 3 — Autonomous Tasks**
```
Autonomous tasks
The ambition: agents that break a goal into steps and execute them
autonomously, correcting course along the way.
```

**Card 4 — Efficiency**
```
Efficiency
An architecture designed to cut compute cost: reasoning in latent space instead
of producing everything as text.
```

---

### 4.6 — Luthor vs a classic chatbot (`#comparaison`)

**Title (H2):**
```
Luthor is not a chatbot
```

| | Classic chatbot | Luthor (Agentic World Model) |
| :--- | :--- | :--- |
| Goal | Generate an answer | Reach a goal |
| Method | Predict the next word | Predict the future state of the world |
| Horizon | One answer at a time | Multi-step planning |
| Memory | Limited to the request context | Persistent internal representation (planned) |
| Output | Text | A decision / an action |

---

### 4.7 — Roadmap / Current status (`#roadmap`)

**Title (H2):**
```
Where Luthor stands
```

**Intro:**
```
Luthor is actively in development. Here, transparently, is what exists today and
what we're building next.
```

**Today (prototype):**
```
— Open-source prototype of the world model (encoder, predictor, planner)
— Trajectory-simulation planning loop (MPC)
— Public technical documentation
```

**In progress:**
```
— Richer predictors and encoders
— Long-term memory and extended planning horizons
— Autonomous agent infrastructure
```

**Next:**
```
— Dedicated app and API (app.luthor.org)
— More complex environments and tasks
— Tools for developers and integrators
```

---

### 4.8 — Foundations & inspiration

**Title (H2):**
```
Grounded in research
```

**Paragraph:**
```
Luthor draws on work around Autonomous Machine Intelligence (AMI) and the Joint
Embedding Predictive Architecture (JEPA) popularized by Yann LeCun:
self-supervised learning, non-generative world models, and cost-guided
planning. A solid theoretical base for building agents that reason.
```

---

### 4.9 — Primary call-to-action

**Title (H2):**
```
Follow Luthor as it's built
```

**Paragraph:**
```
The project is open and moving fast. Explore the code, follow the progress, or
reach out to talk about it.
```

**Primary button:**
```
Explore on GitHub
```
(link → `https://github.com/ChawnRob/Luthor`)

**Secondary button:**
```
Get in touch
```
(link → `mailto:contact@luthor.org`)

---

### 4.10 — Footer / Contact (`#contact`)

```
Luthor — Agentic World Model
Actively in development · Open source

GitHub: github.com/ChawnRob/Luthor
Contact: contact@luthor.org

© Luthor. Inspired by AMI / JEPA principles.
```

---

## 5. Checklist Squarespace

### 5.1 — Pages à créer
- [ ] **Home** (`luthor.org`) — la one-pager décrite ci-dessus (V1).
- [ ] **404 / Not Found** — page d'erreur sobre, même thème sombre.
- [ ] *(Optionnel V1.1)* **Page EN** — soit une page séparée `/en`, soit un toggle de langue. En V1, on peut publier d'abord la version FR (ou EN) et garder l'autre prête à coller.
- [ ] *(Plus tard)* **Blog / Updates** — pour communiquer l'avancement sans toucher au code.

> Ne **pas** créer de page « Pricing » ni « Product » tant qu'il n'y a pas d'offre réelle.

### 5.2 — Blocs Squarespace à utiliser (par section)
| Section | Bloc(s) recommandé(s) |
| :--- | :--- |
| Hero | Section avec **Background** (couleur/dégradé ou image) + **Text** (badge + H1 + sous-titre) + 2 **Buttons** |
| Proposition de valeur | **Text block** centré |
| Différence | **Text block** + (optionnel) **Image** abstraite |
| Piliers | **Card / Summary grid** ou 4 colonnes (Auto Layout), une carte par pilier |
| Comparaison | **Markdown block** (tableau) ou **Table block**, sinon grille 2 colonnes |
| Roadmap | **Accordion block** (3 entrées : Aujourd'hui / En cours / Ensuite) ou 3 colonnes |
| Fondements | **Text block** |
| CTA | Section accentuée + **Text** + 2 **Buttons** |
| Footer | **Footer Section** Squarespace (texte + liens) |

### 5.3 — Ordre des sections (rappel)
1. Hero → 2. Proposition de valeur → 3. Différence → 4. Piliers → 5. Comparaison → 6. Roadmap → 7. Fondements → 8. CTA → 9. Footer.

### 5.4 — Liens à prévoir
- [ ] GitHub : `https://github.com/ChawnRob/Luthor`
- [ ] Contact : `mailto:contact@luthor.org` *(à confirmer : adresse réelle)*
- [ ] Ancres internes : `#vision`, `#difference`, `#piliers`, `#comparaison`, `#roadmap`, `#contact`
- [ ] *(Préparé, pas encore actif)* Futur lien app : `https://app.luthor.org` → **ne pas publier** tant que l'app n'est pas en ligne (ou afficher un état « Bientôt »).

### 5.5 — Domaines & séparation des environnements
- [ ] `luthor.org` → **Squarespace** (vitrine V1). C'est l'objet de ce document.
- [ ] `app.luthor.org` → **réservé à la future application / API** (Cloud Run). À configurer via un **sous-domaine** dans Squarespace (DNS) **quand** l'app sera prête. Ne pas rediriger tant que rien n'est déployé.
- [ ] Conserver Cloud Run **inchangé** : ce document ne modifie pas le déploiement existant.

### 5.6 — Réglages SEO / méta (Squarespace → Settings)
- [ ] **Titre du site** : `Luthor — Agentic World Model`
- [ ] **Description SEO** : `Luthor est un Agentic World Model open source : planification, mémoire et tâches autonomes, inspiré des principes JEPA. Projet en construction avancée.`
- [ ] **Image de partage social** (Open Graph) : visuel sombre avec le logo + accent cyan.
- [ ] **Favicon** : « L » sur fond charcoal.

---

## 6. Garde-fous (rappel des contraintes)

- ✅ **Aucune modification de code** : ce document est la seule livraison.
- ✅ **Pas de nettoyage Manus** maintenant (hors périmètre).
- ✅ **Cloud Run inchangé.**
- ✅ **Aucune fonctionnalité présentée comme « en production »** si elle ne l'est pas (formulations « visée », « en cours », « l'ambition »).
- ✅ **LUTHOR positionné comme projet en construction avancée**, pas comme produit fini.
- ✅ **Vision claire** : Agentic World Model → planning, memory, autonomous tasks.
- ✅ **COCO / OpenChawn** : volontairement **absent** de cette vitrine (séparation stricte).
