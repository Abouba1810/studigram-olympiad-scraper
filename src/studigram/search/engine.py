from studigram.models import Result
from studigram.scrapers import SCRAPERS


SCRAPER_MAP = {
    "ioai": "IOAI",
    "imo": "IMO",
    "ioi": "IOI",
    "ipho": "IPhO",
    "icho": "IChO",
}


class SearchEngine:

    def __init__(
        self,
        olympiads: list[str] | None = None,
    ):

        if olympiads is None:
            self.scrapers = [
                scraper_class()
                for scraper_class in SCRAPERS
            ]

        else:

            requested = {
                olympiad.lower()
                for olympiad in olympiads
            }

            self.scrapers = [
                scraper_class()
                for scraper_class in SCRAPERS
                if scraper_class.olympiad.lower() in requested
            ]

    def search(
        self,
        name: str,
    ) -> list[Result]:

        results = []

        for scraper in self.scrapers:

            try:

                found = scraper.search(name)

                results.extend(found)

            except Exception as error:

                print(
                    f"[ERROR] {scraper.olympiad}: {error}",
                    flush=True,
                )

        return self._sort_results(results)

    @staticmethod
    def _sort_results(
        results: list[Result],
    ) -> list[Result]:

        return sorted(
            results,
            key=lambda result: (
                result.year,
                result.olympiad,
            ),
            reverse=True,
        )