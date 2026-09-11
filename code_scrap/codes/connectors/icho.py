import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def normalize(text):
    return " ".join(
        text.strip().lower().split()
    )


def search_icho(full_name, source):

    target = normalize(full_name)

    url = source["search_url"]

    results = []

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print(
            f"      IChO network error: {error}"
        )

        return results

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Certaines versions de la page
    # utilisent un formulaire GET.
    forms = soup.find_all("form")

    search_url = url

    for form in forms:

        action = form.get("action")

        if action:

            if action.startswith("http"):
                search_url = action

            else:
                search_url = (
                    "https://www.icho-official.org"
                    + "/"
                    + action.lstrip("/")
                )

    # Tentative GET avec différents noms
    # de paramètres utilisés par les formulaires.

    possible_parameters = [
        {"name": full_name},
        {"Name": full_name},
        {"q": full_name},
        {"search": full_name}
    ]

    for params in possible_parameters:

        try:

            response = requests.get(
                search_url,
                params=params,
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

                if len(values) < 4:
                    continue

                if target != normalize(values[0]):
                    continue

                name = values[0]
                year = values[2]
                country = values[3]
                award = (
                    values[4]
                    if len(values) > 4
                    else ""
                )

                medal = None

                award_lower = award.lower()

                if "gold" in award_lower:
                    medal = "Gold"

                elif "silver" in award_lower:
                    medal = "Silver"

                elif "bronze" in award_lower:
                    medal = "Bronze"

                elif "honourable" in award_lower:
                    medal = "Honourable Mention"

                results.append({
                    "full_name": name,
                    "country": country,
                    "olympiad": "IChO",
                    "year": year,
                    "medal": medal,
                    "rank": None,
                    "score": None,
                    "award": award,
                    "source_url": search_url
                })

        if results:
            break

    return results