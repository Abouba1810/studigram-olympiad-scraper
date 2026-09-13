# Studigram Olympiad Scraper

Search engine for international olympiad results.

## Supported Olympiads

- **IOAI** — International Olympiad in Artificial Intelligence
- **IMO** — International Mathematical Olympiad
- **IOI** — International Olympiad in Informatics
- **IPhO** — International Physics Olympiad
- **IChO** — International Chemistry Olympiad

## Features

- Search participants by name
- Search across all supported olympiads
- Search a specific olympiad using CLI flags
- Fuzzy name matching
- Protection against false-positive name matches
- Support for multiple competition years
- Normalized result format
- JSON output
- Source URL included with every result
- Modular scraper architecture
- Search engine designed to be reused by a future REST API

## Architecture

The project separates:

- result models
- olympiad scrapers
- name matching
- HTTP utilities
- search engine
- CLI

```text
studigram-olympiad-scraper/
│
├── src/
│   └── studigram/
│       ├── __init__.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   └── result.py
│       │
│       ├── scrapers/
│       │   ├── __init__.py
│       │   ├── ioai.py
│       │   ├── imo.py
│       │   ├── ioi.py
│       │   ├── ipho.py
│       │   └── icho.py
│       │
│       ├── search/
│       │   ├── __init__.py
│       │   └── engine.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── http.py
│           └── names.py
│
├── scripts/
│   └── search.py
│
├── data/
│   └── cache/
│
├── requirements.txt
├── pyproject.toml
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Abouba1810/studigram-olympiad-scraper.git
cd studigram-olympiad-scraper
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

For development, install the project in editable mode:

```bash
pip install -e .
```

## Usage

### Search all olympiads

Search for a participant across all supported olympiads:

```bash
python3 scripts/search.py "Aboubacar Diarra"
```

The search engine automatically checks all available olympiad scrapers and returns the matching results as JSON.

### Search only IOAI

```bash
python3 scripts/search.py "Aboubacar Diarra" --ioai
```

### Search only IMO

```bash
python3 scripts/search.py "Jonathan He" --imo
```

### Search only IOI

```bash
python3 scripts/search.py "Jonathan He" --ioi
```

### Search only IPhO

```bash
python3 scripts/search.py "Jonathan He" --ipho
```

### Search only IChO

```bash
python3 scripts/search.py "Jonathan He" --icho
```

## Output

All scrapers return results using the same normalized schema.

Example:

```json
[
  {
    "full_name": "Aboubacar Diarra",
    "country": "Mali 1",
    "olympiad": "IOAI",
    "year": 2026,
    "medal": "Bronze",
    "rank": 140,
    "score": 81.6694,
    "award": "Bronze",
    "source_url": "https://ioai-official.org/republic-of-kazakhstan/results-2026/"
  }
]
```

## Result Schema

| Field | Type | Description |
|---|---|---|
| `full_name` | `string` | Participant's full name |
| `country` | `string` | Country or delegation |
| `olympiad` | `string` | Olympiad identifier |
| `year` | `integer` | Competition year |
| `medal` | `string \| null` | Medal obtained by the participant |
| `rank` | `integer \| null` | Overall ranking |
| `score` | `float \| null` | Participant's score |
| `award` | `string \| null` | Official award |
| `source_url` | `string` | Original source of the result |

## Name Matching

The search engine normalizes participant names before comparing them.

It handles:

- capitalization differences
- accents and diacritics
- extra spaces
- small spelling differences

The matcher also checks first names and surnames separately to reduce false positives.

For example:

```text
Aboubacar Diarra
```

should not incorrectly match:

```text
Aboubacar Bangoura
```

while small spelling variations can still be detected.

## Multiple Years

The scrapers can search across multiple competition years.

For example:

```bash
python3 scripts/search.py "Vladislav Zhiganov" --ioi
```

can return both the 2026 and 2025 results:

```json
[
  {
    "full_name": "Vladislav Zhiganov",
    "country": "",
    "olympiad": "IOI",
    "year": 2026,
    "medal": "Gold",
    "rank": 2,
    "score": 482.75,
    "award": "Gold",
    "source_url": "https://stats.ioinformatics.org/results/2026"
  },
  {
    "full_name": "Vladislav Zhiganov",
    "country": "",
    "olympiad": "IOI",
    "year": 2025,
    "medal": "Gold",
    "rank": 25,
    "score": 447.86,
    "award": "Gold",
    "source_url": "https://stats.ioinformatics.org/results/2025"
  }
]
```

The `rank` is specific to each competition year.

## Data Sources

Each scraper retrieves data from the official or primary source available for its olympiad.

Every result contains a `source_url` field pointing to the page from which the result was retrieved.

This makes it possible to verify individual results against the original source.

## Search Engine

The main search engine is implemented through `SearchEngine`.

Example:

```python
from studigram.search import SearchEngine

engine = SearchEngine()

results = engine.search("Aboubacar Diarra")

for result in results:
    print(result.to_dict())
```

A specific set of olympiads can also be selected:

```python
engine = SearchEngine(
    olympiads=["IOAI", "IOI"]
)

results = engine.search("Aboubacar Diarra")
```

## Development

Install the project in editable mode:

```bash
pip install -e .
```

Run a search:

```bash
python3 scripts/search.py "Aboubacar Diarra"
```

Run an IOI search:

```bash
python3 scripts/search.py "Jonathan He" --ioi
```

The CLI outputs JSON only, making the result easy to consume by other programs or a future API.

## Roadmap

- Improve scraper reliability
- Improve coverage of historical results
- Add automated tests
- Add caching
- Add more international olympiads
- Improve error handling
- Add a REST API
- Build the Studigram participant search interface
- Integrate the search engine into Studigram

## Project

Studigram Olympiad Scraper is developed as part of **Studigram**, a project focused on making academic and olympiad achievements easier to search and explore.

## License

This project is part of Studigram.