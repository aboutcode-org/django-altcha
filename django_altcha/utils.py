# Django
from django.templatetags.static import static


def lazy_static(path):
    """
    Return a lazy proxy that resolves static(path) when stringified (e.g. in templates).
    This is useful to avoid AppRegistryNotReady errors in settings.
    """

    class _LazyStaticUrl:
        __slots__ = ("_path",)

        def __init__(self, path):
            self._path = path

        def __str__(self):
            return static(self._path)

    return _LazyStaticUrl(path)
