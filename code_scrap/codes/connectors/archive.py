import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def normalize(text):
    return " ".join(
        text.strip().lower().split()
    )


def search_archive(
    full_name,
    source,
    olympiad
):

    target = normalize(full_name)

    results = []

    base_url = source["base_url"]

    try:

        response = requests.get(
            base_url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print(
            f"      {olympiad} network error: {error}"
        )

        return results

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    pages = {
        base_url
    }

    # Récupération des pages internes
    # contenant potentiellement résultats,
    # archives, contestants, participants, etc.

    for link in soup.find_all("a"):

        text = link.get_text(
            " ",
            strip=True
        ).lower()

        href = link.get("href")

        if not href:
            continue

        keywords = [
            "result",
            "archive",
            "participant",
            "contestant",
            "hall",
            "history",
            "year"
        ]

        if any(
            keyword in text
            or keyword in href.lower()
            for keyword in keywords
        ):

            pages.add(
                urljoin(
                    base_url,
                    href
                )
            )

    # Limitation volontaire :
    # on ne visite pas des centaines de pages
    # arbitrairement.

    for url in list(pages)[:50]:

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            response.raise_for_status()

        except requests.RequestException:

            continue

        content_type = (
            response.headers
            .get("Content-Type", "")
            .lower()
        )

        # Pour cette V1, on traite seulement HTML.
        # Les PDF auront un connecteur dédié ensuite.

        if "html" not in content_type:

            continue

        page = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for table in page.find_all("table"):

            for row in table.find_all("tr"):

                cells = row.find_all(
                    ["td", "th"]
                )

                values = [
                    cell.get_text(
                        " ",
                        strip=True
                    )
                    for cell in cells
                ]

                if not values:
                    continue

                normalized = [
                    normalize(value)
                    for value in values
                ]

                if target not in normalized:
                    continue

                index = normalized.index(
                    target
                )

                results.append({
                    "full_name": values[index],
                    "country": None,
                    "olympiad": olympiad,
                    "year": None,
                    "medal": None,
                    "rank": None,
                    "score": None,
                    "award": None,
                    "source_url": url
                })

    return results