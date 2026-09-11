from .archive import search_archive


def search_ibo(full_name, source):

    return search_archive(
        full_name,
        source,
        "IBO"
    )