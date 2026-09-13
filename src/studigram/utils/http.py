import requests


HEADERS = {
    "User-Agent": (
        "Studigram-Olympiad-Research/1.0 "
        "(https://github.com/Abouba1810/studigram-olympiad-scraper)"
    )
}


def get(url: str) -> requests.Response:
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response