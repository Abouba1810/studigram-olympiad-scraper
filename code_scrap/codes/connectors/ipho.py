import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def normalize(text):
    return " ".join(
        text.strip().lower().split()
    )


def search_ipho(full_name, source):

    target = normalize(full_name)

    results = []

    url = source["search_url"]

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print(
            f"      IPhO network error: {error}"
        )

        return results

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Recherche dans tous les liens
    # et textes rendus par la page.

    for table in soup.find_all("table"):

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

            if len(values) < 4:
                continue

            if normalize(values[0]) != target:
                continue

            name = values[0]
            year = values[1]
            country = values[2]
            award = values[3]

            medal = None

            lower = award.lower()

            if "gold" in lower:
                medal = "Gold"

            elif "silver" in lower:
                medal = "Silver"

            elif "bronze" in lower:
                medal = "Bronze"

            elif "honourable" in lower:
                medal = "Honourable Mention"

            results.append({
                "full_name": name,
                "country": country,
                "olympiad": "IPhO",
                "year": year,
                "medal": medal,
                "rank": None,
                "score": None,
                "award": award,
                "source_url": url
            })

    return results