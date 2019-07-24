class EnhancedDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DictOpreating:
    @staticmethod
    def enhance(origin: dict) -> EnhancedDict:
        if type(origin) != dict:
            return origin

        def change(old: dict):
            new = EnhancedDict()
            for key, value in old.items():
                new[key] = \
                    EnhancedDict(change(value)) if type(value) == dict else value

        return change(origin)

    @staticmethod
    def weaken(origin: EnhancedDict) -> dict:
        if type(origin) != EnhancedDict:
            return origin

        def change(old: EnhancedDict):
            new = dict()
            for key, value in old.items():
                new[key] = \
                    dict(change(value)) if type(value) == EnhancedDict else value
            return new

        return change(origin)