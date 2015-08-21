from functools import lru_cache


class MementoMetaclass(type):
    @lru_cache(maxsize=None)
    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)
