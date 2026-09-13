import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from studigram.models import Result
from studigram.utils.http import get
from studigram.utils.names import is_name_match


class IChOScraper:

    olympiad = "IChO"

    SEARCH_URL = (
        "https://www.icho-official.org/"
        "results/seek.php"
    )

    def search(self, name: str) -> list[Result]:

        results = []

        urls = [
            self.SEARCH_URL
            + "?name="
            + quote(name),

            self.SEARCH_URL
            + "?q="
            + quote(name),
        ]

        for url in urls:

            try:
                response = get(url)
            except Exception:
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            found = self._parse_search_page(
                soup,
                name,
                response.url,
            )

            results.extend(found)

            if results:
                break

        return self._deduplicate(results)

    def _parse_search_page(
        self,
        soup: BeautifulSoup,
        target_name: str,
        source_url: str,
    ) -> list[Result]:

        results = []

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

            if not self._is_result_table(headers):
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

                if len(cells) < len(headers):
                    continue

                data = dict(zip(headers, cells))

                result = self._parse(
                    data,
                    source_url,
                )

                if result is None:
                    continue

                if is_name_match(
                    target_name,
                    result.full_name,
                ):
                    results.append(result)

        return results

    @staticmethod
    def _is_result_table(
        headers: list[str],
    ) -> bool:

        joined = " ".join(headers)

        return (
            "contestant" in joined
            and "year" in joined
        )

    def _parse(
        self,
        data: dict,
        source_url: str,
    ) -> Result | None:

        full_name = self._find(
            data,
            [
                "contestant",
                "name",
            ],
        )

        if not full_name:
            return None

        country = self._find(
            data,
            [
                "country",
                "nation",
            ],
        ) or ""

        year = self._find(
            data,
            ["year"],
        )

        award = self._find(
            data,
            [
                "award",
                "medal",
            ],
        )

        rank = self._find(
            data,
            ["rank"],
        )

        if not year:
            return None

        match = re.search(
            r"\d{4}",
            year,
        )

        if not match:
            return None

        year_int = int(match.group())

        return Result(
            full_name=full_name,
            country=country,
            olympiad="IChO",
            year=year_int,
            medal=self._extract_medal(award),
            rank=self._parse_rank(rank),
            score=None,
            award=award,
            source_url=source_url,
        )

    @staticmethod
    def _clean_header(value: str) -> str:

        value = value.lower().strip()

        return re.sub(
            r"\s+",
            " ",
            value,
        )

    @staticmethod
    def _find(
        data: dict,
        keys: list[str],
    ) -> str | None:

        for key in keys:

            if key in data and data[key]:
                return data[key].strip()

        return None

    @staticmethod
    def _parse_rank(value: str | None):

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
    def _extract_medal(value: str | None):

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