import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}


def normalize(text):
    return " ".join(
        text.strip().lower().split()
    )


def fetch(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def extract_tables(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    return soup.find_all("table")


def search_ioai(full_name, source):

    target = normalize(full_name)

    results = []

    year_urls = {
        2024:
            "https://ioai-official.org/bulgaria-2024/results/",
        2025:
            "https://ioai-official.org/china-2025/results-2025/",
        2026:
            "https://ioai-official.org/republic-of-kazakhstan/results-2026/"
    }

    for year in source.get("years", []):

        url = year_urls.get(year)

        if not url:
            continue

        print(f"    → IOAI {year}")

        try:
            html = fetch(url)

        except requests.RequestException as error:
            print(f"      Network error: {error}")
            continue

        tables = extract_tables(html)

        for table in tables:

            rows = table.find_all("tr")

            for row in rows:

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

                normalized_values = [
                    normalize(value)
                    for value in values
                ]

                if target not in normalized_values:
                    continue

                # 2025 / 2026 individual tables
                if len(values) >= 5:

                    name_index = None

                    for i, value in enumerate(
                        normalized_values
                    ):

                        if value == target:
                            name_index = i
                            break

                    if name_index is None:
                        continue

                    name = values[name_index]

                    # 2026:
                    # rank | name | team | tasks... | total | award
                    #
                    # 2025:
                    # rank | name | country | tasks... | total | medal

                    rank = values[0]

                    country = (
                        values[2]
                        if len(values) > 2
                        else None
                    )

                    total = (
                        values[-2]
                        if len(values) >= 2
                        else None
                    )

                    award = values[-1]

                    if "🇲🇱" in country:
                        country = country.replace(
                            "🇲🇱",
                            ""
                        ).strip()

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
                        "olympiad": "IOAI",
                        "year": year,
                        "medal": medal,
                        "rank": rank,
                        "score": total,
                        "award": award,
                        "source_url": url
                    })

    return results