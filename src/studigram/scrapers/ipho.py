import re

from bs4 import BeautifulSoup

from studigram.models import Result
from studigram.utils.http import get
from studigram.utils.names import is_name_match


class IPhOScraper:

    olympiad = "IPhO"

    YEARS = range(2000, 2027)

    BASE_URL = (
        "https://ipho-unofficial.org/"
        "timeline/{year}/individual"
    )

    def search(self, name: str) -> list[Result]:

        results = []

        for year in self.YEARS:

            url = self.BASE_URL.format(
                year=year
            )

            try:
                response = get(url)
            except Exception:
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

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

                if "contestant" not in headers:
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
                        year,
                        url,
                    )

                    if result is None:
                        continue

                    if is_name_match(
                        name,
                        result.full_name,
                    ):
                        results.append(result)

        return results

    def _parse(
        self,
        data: dict,
        year: int,
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
            ["country"],
        ) or ""

        rank = self._find(
            data,
            ["rank"],
        )

        award = self._find(
            data,
            ["award"],
        )

        score = self._find(
            data,
            [
                "total",
                "score",
            ],
        )

        return Result(
            full_name=full_name,
            country=country,
            olympiad="IPhO",
            year=year,
            medal=self._extract_medal(award),
            rank=self._parse_rank(rank),
            score=self._parse_score(score),
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
    def _parse_score(value: str | None):

        if not value:
            return None

        value = value.replace(",", ".")

        try:
            return float(value)
        except ValueError:
            return None

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