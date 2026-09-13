from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class Result:
    full_name: str
    country: str
    olympiad: str
    year: int
    medal: Optional[str]
    rank: Optional[int]
    score: Optional[float]
    award: Optional[str]
    source_url: str

    def to_dict(self) -> dict:
        return asdict(self)