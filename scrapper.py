import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import re


HEADERS = {
    "User-Agent": "Studigram-Olympiad-Research/1.0"
}


def normalize_name(name):
    """Normalise un nom pour faciliter le matching."""

    name = name.lower().strip()

    # Supprimer accents
    import unicodedata

    name = unicodedata.normalize("NFD", name)
    name = "".join(
        c for c in name
        if unicodedata.category(c) != "Mn"
    )

    # Supprimer caractères spéciaux
    name = re.sub(r"[^a-z0-9 ]", " ", name)

    # Supprimer espaces multiples
    name = re.sub(r"\s+", " ", name)

    return name


def name_similarity(name1, name2):
    """
    Compare deux noms.

    Exemple:
    'Gennady Korotkevich'
    'Korotkevich Gennady'
    """

    a = normalize_name(name1)
    b = normalize_name(name2)

    # comparaison normale
    score1 = fuzz.ratio(a, b)

    # comparaison tokenisée
    score2 = fuzz.token_sort_ratio(a, b)

    return max(score1, score2)


def scrape_table(url, olympiad):
    """
    Scrape toutes les tables HTML d'une page.
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    results = []

    for table in soup.find_all("table"):

        rows = table.find_all("tr")

        if not rows:
            continue

        headers = [
            cell.get_text(" ", strip=True).lower()
            for cell in rows[0].find_all(
                ["th", "td"]
            )
        ]

        for row in rows[1:]:

            cells = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all(
                    ["td", "th"]
                )
            ]

            if len(cells) != len(headers):
                continue

            data = dict(zip(headers, cells))

            results.append({
                "olympiad": olympiad,
                "raw": data
            })

    return results


def extract_name(data):
    """
    Essaie de trouver la colonne contenant le nom.
    """

    possible = [
        "name",
        "contestant",
        "participant",
        "student"
    ]

    for key in possible:

        if key in data:
            return data[key]

    # Cas IOI avec First Name / Last Name
    first = data.get("first name", "")
    last = data.get("last name", "")

    if first or last:
        return f"{first} {last}".strip()

    return None


def extract_country(data):

    possible = [
        "country",
        "nation",
        "country name"
    ]

    for key in possible:

        if key in data:
            return data[key]

    return None


def extract_medal(data):

    possible = [
        "medal",
        "award",
        "medals",
        "prize"
    ]

    for key in possible:

        if key in data:
            return data[key]

    return None


def search_results(target_name, results):

    matches = []

    for result in results:

        data = result["raw"]

        candidate = extract_name(data)

        if not candidate:
            continue

        score = name_similarity(
            target_name,
            candidate
        )

        if score >= 80:

            matches.append({
                "name": candidate,
                "country": extract_country(data),
                "medal": extract_medal(data),
                "olympiad": result["olympiad"],
                "similarity": score,
                "raw": data
            })

    return sorted(
        matches,
        key=lambda x: x["similarity"],
        reverse=True
    )