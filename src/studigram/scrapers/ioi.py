import re

from bs4 import BeautifulSoup

from studigram.models import Result
from studigram.utils.http import get
from studigram.utils.names import is_name_match


class IOIScraper:

    olympiad = "IOI"

    YEARS = range(2000, 2027)

    CONTESTANTS_URL = (
        "https://stats.ioinformatics.org/"
        "contestants/{year}"
    )

    RESULTS_URL = (
        "https://stats.ioinformatics.org/"
        "results/{year}"
    )

    def search(self, name: str) -> list[Result]:

        results = []

        for year in self.YEARS:


            contestants_url = self.CONTESTANTS_URL.format(
                year=year
            )

            results_url = self.RESULTS_URL.format(
                year=year
            )

            # ==================================================
            # 1. PARTICIPANTS
            # ==================================================

            try:
                response = get(contestants_url)
            except Exception:
                continue

            contestants_soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            contestants = self._find_contestants(
                contestants_soup,
                name,
            )

            if not contestants:
                continue

            # ==================================================
            # 2. RÉSULTATS
            # ==================================================

            try:
                response = get(results_url)
            except Exception:
                response = None

            if response is None:

                for contestant in contestants:

                    results.append(
                        Result(
                            full_name=contestant["full_name"],
                            country=contestant["country"],
                            olympiad="IOI",
                            year=year,
                            medal=None,
                            rank=None,
                            score=None,
                            award=None,
                            source_url=contestants_url,
                        )
                    )

                continue

            results_soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            found = self._find_results(
                results_soup,
                contestants,
                year,
                results_url,
            )

            if found:
                results.extend(found)

            else:

                for contestant in contestants:

                    results.append(
                        Result(
                            full_name=contestant["full_name"],
                            country=contestant["country"],
                            olympiad="IOI",
                            year=year,
                            medal=None,
                            rank=None,
                            score=None,
                            award=None,
                            source_url=contestants_url,
                        )
                    )

        return self._deduplicate(results)

    # ==========================================================
    # CONTESTANTS
    # ==========================================================

    def _find_contestants(
        self,
        soup: BeautifulSoup,
        target_name: str,
    ) -> list[dict]:

        contestants = []

        for table in soup.find_all("table"):

            rows = table.find_all("tr")

            if len(rows) < 2:
                continue

            headers = [
                self._clean_header(
                    cell.get_text(
                        " ",
                        strip=True,
                    )
                )
                for cell in rows[0].find_all(
                    ["th", "td"]
                )
            ]

            name_index = self._find_column(
                headers,
                [
                    "contestant",
                    "name",
                ],
            )

            if name_index is None:
                continue

            country_index = self._find_column(
                headers,
                [
                    "member",
                    "country",
                ],
            )

            for row in rows[1:]:

                cells = [
                    cell.get_text(
                        " ",
                        strip=True,
                    )
                    for cell in row.find_all(
                        ["td", "th"]
                    )
                ]

                if len(cells) <= name_index:
                    continue

                full_name = cells[name_index].strip()

                if not full_name:
                    continue

                if not is_name_match(
                    target_name,
                    full_name,
                ):
                    continue

                country = ""

                if (
                    country_index is not None
                    and len(cells) > country_index
                ):
                    country = cells[
                        country_index
                    ].strip()

                contestants.append(
                    {
                        "full_name": full_name,
                        "country": country,
                    }
                )

        return contestants

    # ==========================================================
    # RESULTS
    # ==========================================================

    def _find_results(
        self,
        soup: BeautifulSoup,
        contestants: list[dict],
        year: int,
        source_url: str,
    ) -> list[Result]:

        results = []

        for table in soup.find_all("table"):

            rows = table.find_all("tr")

            if len(rows) < 2:
                continue

            for row in rows[1:]:

                cells = [
                    cell.get_text(
                        " ",
                        strip=True,
                    )
                    for cell in row.find_all(
                        ["td", "th"]
                    )
                ]

                # Structure IOI actuelle :
                #
                # 0  Rank
                # 1  Contestant
                # 2  Member
                # 3  B
                # 4  M
                # 5  T
                # 6  C
                # 7  M
                # 8  P
                # 9  Score Abs.
                # 10 Score Rel.
                # 11 Award
                #
                # Exemple :
                #
                # 7
                # Jonathan He
                # United States of America
                # ...
                # 436.15
                # 72.69%
                # Gold

                if len(cells) < 12:
                    continue

                full_name = cells[1].strip()

                if not full_name:
                    continue

                contestant = self._find_matching_contestant(
                    full_name,
                    contestants,
                )

                if contestant is None:
                    continue

                rank = self._parse_rank(
                    cells[0]
                )

                country = cells[2].strip()

                if not country:
                    country = contestant["country"]

                score = self._parse_score(
                    cells[9]
                )

                award = cells[11].strip()

                if not award:
                    award = None

                results.append(
                    Result(
                        full_name=full_name,
                        country=country,
                        olympiad="IOI",
                        year=year,
                        medal=self._extract_medal(
                            award
                        ),
                        rank=rank,
                        score=score,
                        award=award,
                        source_url=source_url,
                    )
                )

        return results

    # ==========================================================
    # MATCHING
    # ==========================================================

    @staticmethod
    def _find_matching_contestant(
        name: str,
        contestants: list[dict],
    ) -> dict | None:

        for contestant in contestants:

            if is_name_match(
                name,
                contestant["full_name"],
            ):
                return contestant

        return None

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def _find_column(
        headers: list[str],
        candidates: list[str],
    ) -> int | None:

        for candidate in candidates:

            for index, header in enumerate(headers):

                if header == candidate:
                    return index

        return None

    @staticmethod
    def _clean_header(
        value: str,
    ) -> str:

        value = value.lower().strip()

        value = value.replace("▲", "")
        value = value.replace("▼", "")

        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()

    @staticmethod
    def _parse_rank(
        value: str | None,
    ) -> int | None:

        if not value:
            return None

        match = re.search(
            r"\d+",
            value,
        )

        if not match:
            return None

        return int(match.group())

    @staticmethod
    def _parse_score(
        value: str | None,
    ) -> float | None:

        if not value:
            return None

        value = value.strip()
        value = value.replace(",", ".")

        match = re.search(
            r"\d+(?:\.\d+)?",
            value,
        )

        if not match:
            return None

        try:
            return float(match.group())

        except ValueError:
            return None

    @staticmethod
    def _extract_medal(
        value: str | None,
    ) -> str | None:

        if not value:
            return None

        value = value.lower()

        if "gold" in value:
            return "Gold"

        if "silver" in value:
            return "Silver"

        if "bronze" in value:
            return "Bronze"

        if "honourable" in value:
            return "Honourable Mention"

        if "honorable" in value:
            return "Honourable Mention"

        return None

    # ==========================================================
    # DEDUPLICATION
    # ==========================================================

    @staticmethod
    def _deduplicate(
        results: list[Result],
    ) -> list[Result]:

        seen = set()
        output = []

        for result in results:

            key = (
                result.full_name.lower(),
                result.olympiad,
                result.year,
            )

            if key in seen:
                continue

            seen.add(key)

            output.append(result)

        return output