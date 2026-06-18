# Note de réflexion — Stratégie d'anonymisation (perso)

> Template à remplir en phase async individuelle (jeudi/vendredi matin).
> **Max 1 page.** Personnel — chaque apprenant rédige la sienne.
> Public : Marianne (évaluation) + futur toi qui relit ce repo.

---

## Ma stratégie d'anonymisation

**Stratégie mix : généralisation + hash pour les PERSON, généralisation pour EMAIL/PHONE/IBAN**

J'applique une **approche différenciée** selon la sensibilité et l'utilité des PII :

- **PERSON (noms)** → hash + généralisation :
  - Remplacer chaque nom détecté par un identifiant haché (avec salt)
  - Mixé avec une généralisation (ex. `PERSON_hash`)
  - **Logique** : garde le contexte RH nécessaire à l'analyse d'augmentations ou d'évolutions

- **EMAIL, PHONE, IBAN** → généralisés par [EMAIL], [PHONE], [IBAN] :
  - Ces trois PII sont **inutiles** dans le contexte RH d'analyse d'augmentations ou d'évolutions.
  - Risque RGPD maximal (coordonnées directes, données financières).

- **ORG, GPE, DATE** → conservation :
  - Les noms d'organisations internes (HR, finance…) **contextualisent** l'action RH.
  - Les lieux (pays, villes) aident à identifier des disparités géographiques ou des patterns d'expatriation.
  - Les dates (même généralisées à l'année ou au trimestre) permettent une analyse temporelle des décisions.
  - Ces trois dimensions apportent une **vraie valeur analytique** pour un modèle prédictif ou un audit éthique.



## Ce que j'ai gardé lisible et pourquoi

- **Dates** (année/trimestre après généralisation) : permettent une analyse temporelle aidant les décisions RH.
- **Organisations internes** (noms de services HR, coaching, etc.) : contextualisent l'action RH et aident à comprendre les processus décisionnels.
- **Entités géopolitiques (GPE)** : utiles pour identifier des disparités géographiques pouvant entrainer des biais liés à l'origine.

## Ce que j'ai masqué et pourquoi

- **Noms de personnes (PERSON)** → remplacement par pseudonymes hachés (`PERSON_[SHA256]`)
  - Les noms sont directement identifiants au sens RGPD; les supprimer complètement enlèverait trop le contexte.
  - La **stratégie mix (hash + généralisation)** préserve la traçabilité interne sans exposer l'identité.

- **Adresses email** → généralisation complète (remplacé par `[EMAIL]`)
  - Donnée hautement sensible (contact direct, souvent personnel).
  - Sans intérêt pour prédire une augmentation ou une carrière.

- **Numéros de téléphone** → généralisation complète (remplacé par `[PHONE]`)
  - Même justification : sensibilité maximale (coordonnée directe), sans intérêt métier.

- **Numéros IBAN partiels** → généralisation complète (remplacé par `[IBAN]`)
  - Expose des données financières même masquées.
  - Sans intérêt pour prédire une augmentation ou une carrière.

## Trade-offs assumés

**J'ai placé le curseur entre pseudonymisation et l'anonymisation stricte.**

- **Lisibilité** : garder ORG, GPE et DATE signifie que les commentaires restent compréhensibles par un auditeur interne; les décisions RH conservent leur contexte.
- **Réversibilité** : généraliser EMAIL/PHONE/IBAN et hasher les PERSON élimine 99 % du risque de re-identification.
- **Cohérence** : cette approche conserve une certaine cohérence pour le métier.
- **Asymétrie assumée** : les noms sont l'information la plus sensible mais impossible à supprimer sans perdre le contexte; le hash + la généralisation est un **compromis acceptable** plutôt qu'une suppression complète (perte du contexte RH) ou qu'une conservation en clair (inacceptable RGPD).

## Cadre réglementaire — RGPD + AI Act

- **RGPD** (données personnelles) : minimisation, finalité, droit à l'effacement.
  - Mon anonymisation y répond par :
    - **Minimisation** : suppression pure de EMAIL/PHONE/IBAN (sans intérêt).
    - **Finalité** : les PERSON hachées et les ORG/GPE/DATE gardées servent l'analyse RH uniquement.
    - **Droit à l'effacement** : le hash même salé entraine une pseudonymisation réversible, le RGPD s'applique donc toujours.

- **AI Act** (règlement UE 2024, risque classé par usage) : un système qui exploite des **commentaires RH**
  pour évaluer des personnes relève du **« haut risque »** (emploi/gestion des travailleurs = Annexe III)
  → exigences renforcées de **qualité des données, traçabilité et supervision humaine**.
  - Mon audit + mon anonymisation y contribuent par :
    - **Qualité des données** : l'audit PII et le nettoyage que j'ai fait garantissent une base d'anonymisation sans suppression du contexte métier nécessaire.
    - **Traçabilité** : le hash+généralisation des noms permet de retracer les décisions individuelles sans exposer directement l'identité.
    - **Supervision humaine** : le dataset anonymisé reste compréhensible (ORG/GPE/DATE conservés) pour qu'un évaluateur humain puisse vérifier les décisions du modèle.

## Limites de ma stratégie

- **Faux négatifs (PII non détectées)** :
  - Noms français ou composés (ex. `Noël Joubert de Lagarde`) : `en_core_web_md` peut les rater.
  - Solution : ajouter un modèle bilingue `fr_core_news_md` en parallèle.

- **Faux positifs (texte normal anonymisé à tort)** :
  - Sigles comme `RH` taggées comme PERSON/ORG par spaCy à tort.
  - Solution : une revue manuelle peut réduire l'impact.

## Si je devais industrialiser

- **Pipeline NER bilingue** : ajouter `fr_core_news_md` en parallèle à `en_core_web_md` pour couvrir les noms français.
- **Human-in-the-loop** : une interface de validation où un opérateur RH valide les noms hachés (sampling 10 %).
- **Versionnement du hash** : stocker clé_version + salt pour permettre le retraçage et la re-anonymisation.
- **Tests de ré-identification** : mesurer le risque résiduel post-anonymisation.

---

*Note rédigée par Romain, 18/06/2026, dans le cadre du brief M2-B2 ATOS.*