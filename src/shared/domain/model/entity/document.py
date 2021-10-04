import abc


class Document(metaclass=abc.ABCMeta):
    TYPE = ''

    @property
    def type(self) -> str:
        if not self.TYPE:
            raise ValueError

        return self.TYPE
