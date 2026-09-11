from .archive import search_archive


def search_egoi(full_name, source):

    return search_archive(
        full_name,
        source,
        "EGOI"
    )