import re

from bs4 import BeautifulSoup

from studigram.models import Result
from studigram.utils.http import get
from studigram.utils.names import is_name_match


class IOAIScraper:

    olympiad = "IOAI"

    URLS = {
        2024: "https://ioai-official.org/bulgaria/results-2024/",
        2025: "https://ioai-official.org/china/results-2025/",
        2026: "https://ioai-official.org/republic-of-kazakhstan/results-2026/",
    }

    def search(self, name: str) -> list[Result]:

        results = []

        for year, url in self.URLS.items():

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
                        cell.get_text(" ", strip=True)
                    )
                    for cell in rows[0].find_all(
                        ["th", "td"]
                    )
                ]

                if "name" not in headers:
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

                    if len(cells) != len(headers):
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

    @staticmethod
    def _clean_header(value: str) -> str:
        value = value.lower().strip()
        return re.sub(r"\s+", " ", value)

    def _parse(
        self,
        data: dict,
        year: int,
        source_url: str,
    ) -> Result | None:

        full_name = self._find(
            data,
            [
                "name",
                "participant",
                "contestant",
            ],
        )

        if not full_name:
            return None

        country = self._find(
            data,
            [
                "team",
                "country",
                "nation",
            ],
        ) or ""

        rank = self._find(
            data,
            [
                "rank",
                "place",
                "position",
            ],
        )

        score = self._find(
            data,
            [
                "total",
                "score",
                "total score",
                "points",
            ],
        )

        award = self._find(
            data,
            [
                "award",
                "medal",
                "medals",
            ],
        )

        return Result(
            full_name=full_name,
            country=country,
            olympiad="IOAI",
            year=year,
            medal=self._extract_medal(award),
            rank=self._parse_rank(rank),
            score=self._parse_score(score),
            award=award,
            source_url=source_url,
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

        match = re.search(r"\d+", value)

        if not match:
            return None

        return int(match.group())

    @staticmethod
    def _parse_score(value: str | None):

        if not value:
            return None

        value = value.strip()
        value = value.replace(" ", "")

        if "," in value and "." not in value:
            value = value.replace(",", ".")

        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _extract_medal(value: str | None):

        if not value:
            return None

        value_lower = value.lower()

        if "gold" in value_lower:
            return "Gold"

        if "silver" in value_lower:
            return "Silver"

        if "bronze" in value_lower:
            return "Bronze"

        if "honourable" in value_lower:
            return "Honourable Mention"

        if "honorable" in value_lower:
            return "Honourable Mention"

        return None