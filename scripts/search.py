import argparse
import json

from studigram.search import SearchEngine


OLYMPIAD_FLAGS = {
    "--ioai": "IOAI",
    "--imo": "IMO",
    "--ioi": "IOI",
    "--ipho": "IPhO",
    "--icho": "IChO",
}


def parse_args():

    parser = argparse.ArgumentParser(
        description="Search international olympiad results."
    )

    parser.add_argument(
        "name",
        nargs="+",
        help="Participant name",
    )

    parser.add_argument(
        "--ioai",
        action="store_true",
        help="Search only IOAI",
    )

    parser.add_argument(
        "--imo",
        action="store_true",
        help="Search only IMO",
    )

    parser.add_argument(
        "--ioi",
        action="store_true",
        help="Search only IOI",
    )

    parser.add_argument(
        "--ipho",
        action="store_true",
        help="Search only IPhO",
    )

    parser.add_argument(
        "--icho",
        action="store_true",
        help="Search only IChO",
    )

    return parser.parse_args()


def main():

    args = parse_args()

    name = " ".join(args.name).strip()

    selected = []

    for flag, olympiad in OLYMPIAD_FLAGS.items():

        attribute = flag[2:]

        if getattr(args, attribute):
            selected.append(olympiad)

    engine = SearchEngine(
        olympiads=selected or None
    )

    results = engine.search(name)

    output = [
        result.to_dict()
        for result in results
    ]

    print(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()