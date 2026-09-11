import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def normalize(text):
    return " ".join(
        text.strip().lower().split()
    )


def search_ioi(full_name, source):

    target = normalize(full_name)

    results = []

    start_year = source.get(
        "start_year",
        1989
    )

    end_year = source.get(
        "end_year",
        2026
    )

    for year in range(
        start_year,
        end_year + 1
    ):

        print(f"    → IOI {year}")

        url = (
            "https://stats.ioinformatics.org/"
            f"olympiads/{year}/"
        )

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            response.raise_for_status()

        except requests.RequestException:
            continue

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Cherche les liens "Contestants"
        links = soup.find_all("a")

        contestants_url = None

        for link in links:

            text = link.get_text(
                " ",
                strip=True
            ).lower()

            if text == "contestants":

                href = link.get("href")

                if href:

                    if href.startswith("http"):
                        contestants_url = href

                    else:
                        contestants_url = (
                            "https://stats.ioinformatics.org"
                            + "/"
                            + href.lstrip("/")
                        )

                    break

        if not contestants_url:
            continue

        try:

            response = requests.get(
                contestants_url,
                headers=HEADERS,
                timeout=30
            )

            response.raise_for_status()

        except requests.RequestException:
            continue

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

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

                if not values:
                    continue

                if target not in [
                    normalize(v)
                    for v in values
                ]:
                    continue

                index = next(
                    (
                        i
                        for i, v in enumerate(values)
                        if normalize(v) == target
                    ),
                    None
                )

                if index is None:
                    continue

                name = values[index]

                results.append({
                    "full_name": name,
                    "country": None,
                    "olympiad": "IOI",
                    "year": year,
                    "medal": None,
                    "rank": None,
                    "score": None,
                    "award": None,
                    "source_url": contestants_url
                })

    return results