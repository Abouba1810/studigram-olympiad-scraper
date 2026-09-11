from .archive import search_archive


def search_egmo(full_name, source):

    return search_archive(
        full_name,
        source,
        "EGMO"
    )