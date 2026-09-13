from .ioai import IOAIScraper
from .imo import IMOScraper
from .ioi import IOIScraper
from .ipho import IPhOScraper
from .icho import IChOScraper


SCRAPERS = [
    IOAIScraper,
    IMOScraper,
    IOIScraper,
    IPhOScraper,
    IChOScraper,
]


__all__ = [
    "IOAIScraper",
    "IMOScraper",
    "IOIScraper",
    "IPhOScraper",
    "IChOScraper",
    "SCRAPERS",
]