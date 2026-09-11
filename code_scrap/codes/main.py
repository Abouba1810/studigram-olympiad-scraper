import json
from pathlib import Path

from connectors.ioai import search_ioai
from connectors.imo import search_imo
from connectors.icho import search_icho
from connectors.ipho import search_ipho
from connectors.ioi import search_ioi

from connectors.ibo import search_ibo
from connectors.ioaa import search_ioaa
from connectors.iol import search_iol
from connectors.ieso import search_ieso
from connectors.egoi import search_egoi
from connectors.egmo import search_egmo


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

SOURCES_FILE = (
    PROJECT_DIR
    / "config"
    / "sources.json"
)

DATA_DIR = (
    PROJECT_DIR
    / "data"
)

RESULTS_FILE = (
    DATA_DIR
    / "results.json"
)


# ============================================================
# CONNECTORS
# ============================================================

CONNECTORS = {

    "ioai": search_ioai,

    "imo": search_imo,

    "icho": search_icho,

    "ipho": search_ipho,

    "ioi": search_ioi,

    "ibo": search_ibo,

    "ioaa": search_ioaa,

    "iol": search_iol,

    "ieso": search_ieso,

    "egoi": search_egoi,

    "egmo": search_egmo
}


# ============================================================
# LOAD SOURCES
# ============================================================

def load_sources():

    if not SOURCES_FILE.exists():

        raise FileNotFoundError(
            f"Sources file not found:\n"
            f"{SOURCES_FILE}"
        )

    with open(
        SOURCES_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if "sources" not in data:

        raise ValueError(
            "sources.json must contain "
            "'sources'."
        )

    return data["sources"]


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# DISPLAY
# ============================================================

def display_result(result):

    medal = result.get(
        "medal"
    )

    if medal == "Gold":
        medal_icon = "🥇"

    elif medal == "Silver":
        medal_icon = "🥈"

    elif medal == "Bronze":
        medal_icon = "🥉"

    else:
        medal_icon = ""

    print()
    print(
        "┌──────────────────────────────────────────────"
    )

    print(
        f"│ {result.get('full_name', 'Unknown')}"
    )

    print(
        f"│ Olympiad : "
        f"{result.get('olympiad', 'Unknown')}"
    )

    print(
        f"│ Year     : "
        f"{result.get('year', 'Unknown')}"
    )

    print(
        f"│ Country  : "
        f"{result.get('country') or 'Unknown'}"
    )

    print(
        f"│ Medal    : "
        f"{medal_icon} "
        f"{medal or 'None'}"
    )

    print(
        f"│ Rank     : "
        f"{result.get('rank') or 'Unknown'}"
    )

    print(
        f"│ Score    : "
        f"{result.get('score') or 'Unknown'}"
    )

    print(
        f"│ Award    : "
        f"{result.get('award') or 'Unknown'}"
    )

    print(
        f"│ Source   : "
        f"{result.get('source_url')}"
    )

    print(
        "└──────────────────────────────────────────────"
    )


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(results):

    unique = []

    seen = set()

    for result in results:

        key = (
            result.get("olympiad"),
            result.get("year"),
            result.get("full_name"),
            result.get("country")
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(
            result
        )

    return unique


# ============================================================
# MAIN SEARCH
# ============================================================

def main():

    print()
    print("=" * 60)
    print("STUDIGRAM")
    print("Scientific Olympiad Search Engine")
    print("=" * 60)
    print()

    full_name = input(
        "Full name: "
    ).strip()

    if not full_name:

        print(
            "\nFull name cannot be empty."
        )

        return

    print()
    print(
        f"Searching for: {full_name}"
    )

    print()

    try:

        sources = load_sources()

    except Exception as error:

        print(
            f"\nConfiguration error:\n{error}"
        )

        return

    all_results = []

    # ========================================================
    # SEARCH EACH OLYMPIAD
    # ========================================================

    for source in sources:

        if not source.get(
            "enabled",
            True
        ):
            continue

        source_id = source.get(
            "id"
        )

        short_name = source.get(
            "short_name",
            source_id
        )

        connector = CONNECTORS.get(
            source_id
        )

        print(
            f"[+] Searching {short_name}..."
        )

        if connector is None:

            print(
                f"    ⚠ No connector"
            )

            continue

        try:

            results = connector(
                full_name,
                source
            )

            if results:

                print(
                    f"    ✓ "
                    f"{len(results)} result(s)"
                )

                all_results.extend(
                    results
                )

            else:

                print(
                    "    - No result"
                )

        except Exception as error:

            print(
                f"    ✗ Error: {error}"
            )

    # ========================================================
    # CLEAN
    # ========================================================

    all_results = remove_duplicates(
        all_results
    )

    # ========================================================
    # SAVE
    # ========================================================

    save_results(
        all_results
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    if not all_results:

        print()
        print(
            f"No result found for:"
        )

        print(
            f"  {full_name}"
        )

        print()

        print(
            "No result does not necessarily "
            "mean no participation."
        )

        print(
            "Some historical archives are "
            "not yet fully indexed."
        )

        return

    print()

    for result in all_results:

        display_result(
            result
        )

    print()
    print(
        f"Total results: "
        f"{len(all_results)}"
    )

    print()
    print(
        f"Saved to:"
    )

    print(
        RESULTS_FILE
    )

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()