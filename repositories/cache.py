import os


class Cache:

    @staticmethod
    def _get_path(key: str) -> str:
        path = tuple(("cache", *key.split(":")))
        for i in range(1, len(path)):
            actual_path = str(os.path.join(*path[:i]))
            if not os.path.exists(actual_path):
                os.makedirs(actual_path)
        return str(os.path.join(*path))

    @classmethod
    async def get(cls, key: str) -> str:
        path = cls._get_path(key)
        # client = cls._infrastructure()
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as file:
            value = file.read()
        return value

    @classmethod
    async def set(cls, key: str, value: any):
        path = cls._get_path(key)
        with open(path, "w", encoding="utf-8") as file:
            file.write(value)
