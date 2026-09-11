import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def normalize(text):
    return " ".join(
        text.strip().lower().split()
    )


def search_imo(full_name, source):

    target = normalize(full_name)

    results = []

    start_year = source.get(
        "start_year",
        1959
    )

    end_year = source.get(
        "end_year",
        2026
    )

    for year in range(
        start_year,
        end_year + 1
    ):

        print(f"    → IMO {year}")

        url = (
            "https://www.imo-official.org/"
            f"year_individual_r.aspx?year={year}"
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
                country = values[1]
                rank = values[-3]
                award = values[-1]
                score = values[-4]

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
                    "olympiad": "IMO",
                    "year": year,
                    "medal": medal,
                    "rank": rank,
                    "score": score,
                    "award": award,
                    "source_url": url
                })

    return results