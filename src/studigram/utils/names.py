import re
import unicodedata

from rapidfuzz import fuzz


def normalize_name(name: str) -> str:
    if not name:
        return ""

    name = name.lower().strip()

    name = unicodedata.normalize("NFD", name)

    name = "".join(
        char
        for char in name
        if unicodedata.category(char) != "Mn"
    )

    name = re.sub(r"[^a-z0-9 ]", " ", name)

    name = re.sub(r"\s+", " ", name)

    return name.strip()


def name_similarity(name1: str, name2: str) -> float:
    """
    Retourne un score de similarité entre 0 et 100.
    """

    a = normalize_name(name1)
    b = normalize_name(name2)

    if not a or not b:
        return 0.0

    # Correspondance exacte
    if a == b:
        return 100.0

    # Comparaisons classiques
    ratio = fuzz.ratio(a, b)
    token_ratio = fuzz.token_sort_ratio(a, b)
    partial_ratio = fuzz.partial_ratio(a, b)

    words_a = a.split()
    words_b = b.split()

    # Pour les noms complets, on veut comparer
    # les différentes parties du nom.
    if len(words_a) == len(words_b):

        word_scores = []

        for word_a in words_a:

            best = max(
                fuzz.ratio(word_a, word_b)
                for word_b in words_b
            )

            word_scores.append(best)

        average_word_score = sum(word_scores) / len(
            word_scores
        )

    else:
        average_word_score = 0.0

    # Le score final privilégie le nom complet.
    return max(
        ratio,
        token_ratio,
        min(
            average_word_score,
            partial_ratio,
        ),
    )


def is_name_match(
    target: str,
    candidate: str,
    threshold: float = 90.0,
) -> bool:

    target_normalized = normalize_name(target)
    candidate_normalized = normalize_name(candidate)

    if not target_normalized or not candidate_normalized:
        return False

    # Exact match
    if target_normalized == candidate_normalized:
        return True

    target_words = target_normalized.split()
    candidate_words = candidate_normalized.split()

    # Pour un nom complet, éviter les faux positifs
    # où seul le prénom est ressemblant.
    if len(target_words) >= 2 and len(candidate_words) >= 2:

        target_last = target_words[-1]
        candidate_last = candidate_words[-1]

        last_name_score = fuzz.ratio(
            target_last,
            candidate_last,
        )

        # Le nom de famille doit lui aussi être
        # raisonnablement proche.
        if last_name_score < 75:
            return False

    score = name_similarity(
        target,
        candidate,
    )

    return score >= threshold