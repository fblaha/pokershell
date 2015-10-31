from functools import lru_cache


class MementoMetaclass(type):
    @lru_cache(maxsize=None)
    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class CommonEqualityMixin(object):
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class CommonReprMixin(object):
    def __repr__(self):
        return repr(self.__dict__)
