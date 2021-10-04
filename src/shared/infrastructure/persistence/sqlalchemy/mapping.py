import abc


class Mapping(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def map_entities(self) -> None:
        raise NotImplementedError
