"""M2-B2 — Fonction d'anonymisation à compléter (phase async individuelle).

Tu choisis ta stratégie et tu la défends dans `reflexion.md` :
- Suppression : remplacer l'entité par `[REDACTED]` ou `[NAME]`
- Substitution : Faker côté apprenant, ré-injection
- Généralisation : remplacer par un rôle (`[MANAGER]`, `[EMPLOYEE]`)
- Hash : empreinte irréversible

Le squelette pose la signature minimale. À toi de remplir.
"""
from __future__ import annotations

import re
import sys
from hashlib import sha256
from pathlib import Path

# Charger le modèle spaCy une seule fois (au module load, pas dans la fonction)
import pandas as pd
import spacy

MODEL_NAME = "en_core_web_md"  # ou "fr_core_news_md" selon ton dataset
HASH_SALT = "atos_m2_b2_salt"  # secret en vrai, env var

try:
    NLP = spacy.load(MODEL_NAME)
except OSError as exc:
    raise RuntimeError(
        "Le modele spaCy 'en_core_web_md' est introuvable. "
        "Installe-le dans le meme environnement que celui qui execute ce module avec : "
        "python -m spacy download en_core_web_md"
    ) from exc

# Regex de complément (spaCy ne couvre pas tout — email, IBAN partiel, téléphone US)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
PHONE_RE = re.compile(r"\b\d{3}[.-]?\d{3}[.-]?\d{4}\b")
IBAN_PARTIAL_RE = re.compile(r"\*{2,}\d{4}")

def _hash(value: str) -> str:
    """Hash court avec sel (8 hex chars suffisent en interne)."""
    return sha256((HASH_SALT + value).encode()).hexdigest()[:8]

def anonymize_comments(text: str) -> str:
    """Anonymise un commentaire manager.

    Args:
        text: Texte libre potentiellement contenant des PII.

    Returns:
        Texte anonymisé selon la stratégie choisie.
    """
    # Détecter les entités avec spaCy (PERSON, GPE, ORG, DATE, LOC)
    doc = NLP(text)
    result = {"PERSON": [], "LOC": []}
    for ent in doc.ents:
        if ent.label_ in result:
            result[ent.label_].append(ent.text)
        if ent.label_ == "PERSON":
            text = text.replace(ent.text, f"[PERSON_{_hash(ent.text)}]")  # Remplacement PERSON par hash court
        # ORG & GPE on laisse telquel
        # if ent.label_ == "GPE":
        #     text = text.replace(ent.text, ...)  # à compléter
        # if ent.label_ == "ORG":
        #     text = text.replace(ent.text, ...)  # à compléter
        # if ent.label_ == "DATE":
        #     text = text.replace(ent.text, ...)  # à compléter
        if ent.label == "LOC":
            text = text.replace(ent.text, "[LOC]")  # à compléter

    # Compléter avec regex (spaCy ne détecte ni email ni IBAN partiel ni tel)
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    text = IBAN_PARTIAL_RE.sub("[IBAN]", text)

    return text


def anonymize_csv_file(input_path: Path) -> Path:
    """Anonymise un fichier CSV en appliquant anonymize_comments() sur la colonne manager_comments.

    Args:
        input_path: Chemin du fichier CSV à anonymiser.

    Returns:
        Chemin du fichier CSV anonymisé (suffixe _anonymized_romain.csv).

    Raises:
        FileNotFoundError: Si le fichier d'entrée n'existe pas.
        ValueError: Si la colonne 'manager_comments' est absente du CSV.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Fichier non trouvé : {input_path}")

    # Charger le CSV
    df = pd.read_csv(input_path)

    # Vérifier que la colonne existe
    if "manager_comments" not in df.columns:
        raise ValueError(
            f"La colonne 'manager_comments' est absente du fichier. "
            f"Colonnes disponibles : {list(df.columns)}"
        )

    # Anonymiser la colonne
    df["manager_comments"] = df["manager_comments"].apply(anonymize_comments)

    # Construire le nom du fichier de sortie
    output_stem = input_path.stem + "_anonymized_romain"
    output_path = input_path.parent / (output_stem + ".csv")

    # Enregistrer le fichier
    df.to_csv(output_path, index=False)
    print(f"✓ Fichier anonymisé enregistré : {output_path}")

    return output_path


if __name__ == "__main__":
    # Test rapide ou usage CLI
    if len(sys.argv) > 1:
        # Utilisation : python anonymize.py <chemin_fichier.csv>
        csv_path = sys.argv[1]
        try:
            result = anonymize_csv_file(csv_path)
            print(f"Succès : {result}")
        except (FileNotFoundError, ValueError) as e:
            print(f"Erreur : {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Test rapide sur un commentaire unique
        sample = (
            "Allison Hill is a strong promotion candidate this year. "
            "Discussed with HR (Rhonda Smith, 651.216.1559). "
            "Budget pre-approved on account ****3503."
        )
        print("Avant :", sample)
        print("Après :", anonymize_comments(sample))