# À propos de LUTHOR — About V1

> **Nature de ce document** : page « About / Why » destinée à la vitrine publique et à la communauté. Il explique **pourquoi** LUTHOR existe, **pourquoi** les modèles du monde, **pourquoi** JEPA, en quoi LUTHOR diffère d'un assistant conversationnel, sa vision long terme, et son **état réel aujourd'hui**.
>
> **Périmètre** : documentation uniquement. Aucun code, aucun backend, aucun changement Cloud Run. Aucun merge automatique.
>
> **Statut à communiquer** : LUTHOR est un **Research Prototype** open source — pas un produit, pas un chatbot, pas un simple wrapper de LLM.
>
> *(Version EN principale en section 8 ; cette page FR fait foi pour le contenu.)*

---

## 1. Pourquoi LUTHOR existe

La plupart des systèmes d'IA grand public aujourd'hui sont d'excellents **générateurs de texte** : on leur pose une question, ils produisent une réponse, un mot après l'autre. C'est puissant, mais cela reste réactif et, fondamentalement, orienté vers la **production de langage** — pas vers la **compréhension d'une situation** ni vers l'**action dans la durée**.

LUTHOR part d'une conviction différente : pour qu'un agent soit réellement utile et autonome, il doit d'abord **se représenter le monde**, **anticiper** ce qui va se passer, puis **planifier** et **agir** en conséquence. Autrement dit, raisonner sur les conséquences avant de répondre.

LUTHOR existe pour explorer cette voie de manière concrète, ouverte et honnête : construire, étape par étape, un **Agentic World Model** — un agent dont le cœur est un modèle du monde, et non un moteur de génération de texte.

---

## 2. Pourquoi les World Models

Un **modèle du monde** (« world model ») est une représentation interne qu'un système apprend de son environnement. Plutôt que de mémoriser des réponses, il apprend **comment le monde évolue** : « si je fais ceci, voilà ce qui arrive probablement ensuite ».

Cette capacité est au cœur de l'intelligence naturelle. Un humain n'a pas besoin d'essayer physiquement dix trajectoires pour traverser une rue : il les **simule mentalement** et choisit la meilleure. Un modèle du monde donne à une IA un équivalent de cette « imagination » :

- **Anticiper** plutôt que réagir.
- **Planifier** sur plusieurs étapes vers un objectif.
- **Généraliser** à des situations nouvelles, parce qu'on modélise la dynamique, pas des cas particuliers.
- **Être plus économe** : raisonner dans un espace abstrait coûte moins cher que tout produire en texte.

Les world models sont aujourd'hui un axe de recherche majeur précisément parce qu'ils adressent ce que les systèmes purement réactifs font mal : la **cohérence dans la durée** et la **planification**.

---

## 3. Pourquoi JEPA

LUTHOR s'appuie sur les principes de la **Joint Embedding Predictive Architecture (JEPA)**, popularisée par Yann LeCun dans sa vision d'une **Autonomous Machine Intelligence (AMI)**.

L'idée clé de JEPA : au lieu de prédire chaque détail brut du futur (chaque pixel, chaque mot), on prédit dans un **espace de représentation abstrait (latent)**. Le modèle apprend à représenter ce qui est **important et prévisible**, et ignore le bruit non pertinent.

Pourquoi c'est intéressant pour LUTHOR :

- **Non génératif** : on ne cherche pas à « dessiner » le futur, mais à en capturer la structure utile à la décision. Plus robuste face à l'incertitude.
- **Apprentissage auto-supervisé** : le modèle apprend la dynamique du monde à partir d'observations, sans étiquetage massif.
- **Aligné avec la planification** : prédire dans l'espace latent permet de simuler des trajectoires d'actions efficacement, ce qui alimente directement un planificateur.

> **Honnêteté technique** : aujourd'hui, l'implémentation JEPA de LUTHOR est un **prototype** (encodeur + prédicteur + planificateur sur un environnement simple). Les principes sont posés ; la montée en puissance (architectures plus riches, mémoire, horizons longs) fait partie de la feuille de route.

---

## 4. Différence avec un assistant conversationnel

LUTHOR **n'est pas un chatbot** et **n'est pas un simple wrapper de LLM**.

| | Assistant conversationnel (LLM) | LUTHOR (Agentic World Model) |
| :--- | :--- | :--- |
| Objectif principal | Générer une réponse | Atteindre un objectif |
| Mécanisme | Prédire le mot suivant | Prédire l'état futur du monde |
| Horizon | Une réponse à la fois | Planification sur plusieurs étapes |
| Représentation | Tokens de texte | Espace latent abstrait |
| Mémoire | Limitée au contexte de la requête | État interne persistant (visé) |
| Sortie | Du texte | Une décision / une action |

**Et les LLM, alors ?** Dans LUTHOR, un modèle de langage est une **couche d'interface optionnelle** : utile pour dialoguer avec l'utilisateur, formuler ou expliquer, brancher des outils. Mais ce n'est **pas le cerveau** du système. Le raisonnement vit dans le modèle du monde, non dans la génération de texte. C'est une distinction volontaire et structurante.

---

## 5. Vision long terme

L'ambition de LUTHOR est de construire des **agents autonomes ancrés dans un modèle du monde**, capables de :

1. **Comprendre** une situation à partir d'observations.
2. **Prédire** comment elle évolue selon les actions possibles.
3. **Planifier** une séquence d'actions vers un objectif.
4. **Agir** et se corriger en fonction des résultats.

`Understand. Predict. Plan. Act.`

À terme, cela suppose une **mémoire persistante** (se souvenir sur le long terme), un **moteur de planification** plus puissant que l'échantillonnage aléatoire, et un **espace de travail d'agents** où ces capacités s'assemblent pour exécuter des tâches autonomes.

Cette vision est délibérément **progressive** : LUTHOR ne prétend pas y être déjà. Le projet est partagé ouvertement, capacité par capacité, pour que la construction soit visible et vérifiable.

> *Note* : un futur **workspace expérimental** pourrait voir le jour pour tester ces agents (par ex. sous un sous-domaine dédié). Ce n'est aujourd'hui **qu'une perspective**, sans service en ligne.

---

## 6. État réel du projet aujourd'hui

En toute transparence, voici l'état actuel — **Research Prototype** :

**Existe aujourd'hui**
- Un **prototype open source** du modèle du monde : encodeur, prédicteur, planificateur (MPC par simulation de trajectoires) sur un environnement de simulation simple.
- Une **infrastructure conteneurisée** déployable (Cloud Run).
- Une **couche LLM enfichable**, agnostique au fournisseur (interface optionnelle).
- Une **documentation** publique (architecture, analyses, vision).

**En cours / planifié**
- Encodeurs et prédicteurs plus riches.
- **Mémoire persistante** et horizons de planification étendus.
- **Moteur de planification** plus avancé.
- **Espace de travail d'agents** et **tâches autonomes**.

**Ce que LUTHOR n'est pas (encore)**
- Pas un produit fini ni un service prêt à l'emploi.
- Pas un assistant conversationnel.
- Pas un système autonome opérationnel sur des tâches réelles complexes.

> Aucune date n'est promise. Les éléments « en cours / planifié » sont des **directions**, pas des livraisons annoncées.

---

## 7. Inspirations & références

- **Yann LeCun** — Autonomous Machine Intelligence (AMI), architectures prédictives à embedding conjoint (JEPA).
- **Recherche sur les world models** — apprentissage de la dynamique pour la planification et le contrôle.
- **Apprentissage auto-supervisé non génératif** — apprendre des représentations utiles sans reconstruire l'observation brute.

LUTHOR est un projet indépendant, **open source**, qui s'inspire de ces travaux sans y être affilié.

---

## 8. About — 🇬🇧 English (primary version)

### Why LUTHOR exists
Most mainstream AI today is great at **generating text**: ask a question, get an answer, one word at a time. That's powerful, but it's reactive and fundamentally oriented toward producing language — not toward **understanding a situation** or **acting over time**. LUTHOR takes a different bet: to be genuinely useful and autonomous, an agent must first **represent the world**, **anticipate** what happens next, then **plan** and **act**. LUTHOR exists to explore that path — openly and honestly — by building an **Agentic World Model**, step by step.

### Why world models
A world model is an internal representation a system learns of its environment — *how the world evolves*, not just stored answers. Like a human mentally simulating how to cross a street, a world model gives an AI a form of imagination: anticipate instead of react, plan over multiple steps, generalize to new situations, and stay compute-efficient by reasoning in an abstract space rather than generating everything as text.

### Why JEPA
LUTHOR builds on the **Joint Embedding Predictive Architecture (JEPA)** from Yann LeCun's vision of **Autonomous Machine Intelligence (AMI)**. JEPA predicts in an **abstract latent space** instead of reconstructing raw detail — capturing what is important and predictable, ignoring noise. It's non-generative, self-supervised, and naturally suited to planning. *Today, LUTHOR's JEPA implementation is a prototype (encoder + predictor + planner on a simple environment); richer architectures, memory, and long horizons are on the roadmap.*

### Not a conversational assistant
LUTHOR is **not a chatbot** and **not a simple LLM wrapper**. A chatbot predicts the next word to produce an answer; LUTHOR predicts the future state of the world to reach a goal. In LUTHOR, a language model is an **optional interface layer** (to talk to users, explain, connect tools) — **not the brain**. Reasoning lives in the world model.

### Long-term vision
Autonomous agents grounded in a world model that **Understand. Predict. Plan. Act.** — supported by persistent memory, a stronger planning engine, and an agent workspace. The vision is deliberately progressive: LUTHOR doesn't claim to be there yet, and shares the build openly, one capability at a time. A future **experimental workspace** may appear to test these agents — a perspective only, with no live service today.

### Where the project stands today (Research Prototype)
**Exists today:** an open-source world-model prototype (encoder, predictor, trajectory-simulation planner) on a simple environment; containerized deployment (Cloud Run); a pluggable, provider-agnostic LLM layer; public documentation.
**In progress / planned:** richer encoders & predictors, persistent memory, extended planning horizons, a stronger planner engine, an agent workspace, autonomous tasks.
**What it is not (yet):** a finished product, a conversational assistant, or an operational autonomous system on complex real-world tasks. No dates are promised.

---

## 9. Garde-fous

- ✅ **Documentation uniquement** — aucun code, backend, provider, ni Cloud Run modifié.
- ✅ **Research Prototype** — aucune impression de produit déjà disponible.
- ✅ **Pas un chatbot, pas un wrapper de LLM** — cœur = Agentic World Model (JEPA/AMI), LLM = interface optionnelle.
- ✅ **Honnêteté** — état réel séparé de la vision ; aucune date promise.
- ✅ **`app.luthor.org`** mentionné seulement comme perspective expérimentale, sans lien actif.
- ✅ **COCO / OpenChawn** — volontairement **absent** (séparation stricte).
